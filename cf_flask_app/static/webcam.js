(function() {
    function streamVideo(mediaStream) {
        video.srcObject = mediaStream;
        video.onloadedmetadata = function(e) {
            video.play();
        }
    }

    function waitForFrame() {
        window.setTimeout(function() {
            grabFrameData();
        }, 100);
    }

    function postImage(imageData) {
        // Post Image Data to Flask
        var postReq = new XMLHttpRequest();
        postReq.open('POST', '/detect_faces', true);
        postReq.responseType = 'json';

        postReq.onload = function(event) {
            faces = postReq.response.faces;
        }

        postReq.send(imageData);
    }

    function grabFrameData() {
        webcamCtx.drawImage(video, 0, 0, webcamCanvas.width, webcamCanvas.height);
        webcamCanvas.toBlob(postImage, 'image/jpeg', 1);

        // webcamCtx.font = '36px serif';
        // webcamCtx.fillText(faces + '   ' + faces.length, 0, 140);

        var imageData = webcamCtx.getImageData(0, 0, webcamCanvas.width, webcamCanvas.height);
        var pixelCopy = imageData.data.slice();

        for (var i = 0; i < faces.length; i++) {
            var face = faces[i];
            var faceX = face[0];
            var faceY = face[1];
            var faceW = face[2];
            var faceH = face[3];

            // Creates a copy so we can change pixels based off original pixels.
            // If we edited imageData pixels, then the neighbouring pixel may be
            // affected (e.g., in a gaussian blur).

            // var convMatrix = [[0, -1, 0], [-1, 4, -1], [0, -1, 0]];
            var convMatrix = [0, -1, 0, -1, 4, -1, 0, -1, 0];

            for (var j = 0; j < imageData.data.length; j++) {
                var coordinates = mapIndexToCoord(j);
                var row = coordinates[0];
                var col = coordinates[1];

                if (col >= faceX && col <= faceX + faceW && row >= faceY && row <= faceY + faceH) {
                    if (j % 4 < 3) {
                        if (filterNum == 0)
                            pixelCopy[j] = 255 - imageData.data[j];
                    }
                }
            }
        };

        // Copies pixelCopy back to imageData
        if (filterNum == 0) {
            for (var j = 0; j < imageData.data.length; j++) {
                imageData.data[j] = pixelCopy[j];
            }
        }

        postDetectCtx.putImageData(imageData, 0, 0);
        if (filterNum == 1) {
            postDetectCtx.fillRect(faceX, faceY, faceW, faceH);
        } else if (filterNum == 2) {
            postDetectCtx.strokeStyle = 'white';
            postDetectCtx.strokeRect(faceX, faceY, faceW, faceH);
        }

        waitForFrame();
    }

    function changeFilter(num) {
        if (num != 3) {
            filterNum = num;
        } else {
            // Toggle mirror
            if (postDetectCanvas.style.transform == 'scale(-1, 1)')
                postDetectCanvas.style.transform = 'scale(1, 1)';
            else if (postDetectCanvas.style.transform == 'scale(1, 1)')
                postDetectCanvas.style.transform = 'scale(-1, 1)';
        }
    }

    function gaussianPDF(x, y, sigmaSq) {
        return 1/(2 * Math.PI * sigmaSq) * Math.exp(-(x*x + y*y)/(2*sigmaSq));
    }

    function gaussianKernel(size, sigmaSq) {
        /* Returns the convolution matrix for a gaussian blur filter */

        // Create an empty matrix of size x size
        var convMatrix = new Array(size);
        for (var i = 0; i < size; i++) {
            convMatrix[i] = new Array(size);
        }

        // Fill the matrix with Gaussian values
        for (var row = 0; row < size; row++) {
            for (var col = 0; col < size; col++) {
                // Create x and y, which are centred versions of row and col
                var x = col - (size - 1)/2;
                var y = row - (size - 1)/2;

                convMatrix[row][col] = gaussianPDF(x, y, sigmaSq);
            }
        }

        // Get sum of elements
        var matrixSum = 0;
        for (row = 0; row < size; row++) {
            for (col = 0; col < size; col++) {
                matrixSum += convMatrix[row][col];
            }
        }

        // Normalize element to sum to one
        for (row = 0; row < size; row++) {
            for (col = 0; col < size; col++) {
                convMatrix[row][col] = convMatrix[row][col]/matrixSum;
            }
        }

        return convMatrix;
    }

    function mapIndexToCoord(index) {
        // Maps the index of a one-dimensional representation of the image
        // to a 2d grid. Returns the row and column values.
        var pixelNum = Math.floor(index/4);

        var pixelRow = Math.floor(pixelNum/webcamCanvas.width);
        var pixelCol = pixelNum % webcamCanvas.width;

        return [pixelRow, pixelCol];
    }

    function mapCoordToIndex(row, col) {
        // Maps the coordinate of a 2d matrix to the index when the matrix
        // is flattened.
        var pixelNum = 4*(webcamCanvas.width*row + col);
        return pixelNum;
    }

    function grabSurroundingPixelIndices(imageArray, row, col, size) {
        // Grab the surrounding pixels to convolve with a filter.
        // row and col indicate the pixel and size indicates the 
        // size of the filter.
        var surroundingPixelArray = [];
               
        for (var i = -(size - 1)/2; i <= (size - 1)/2; i++) {
            for (var j = -(size - 1)/2; j <= (size - 1)/2; j++) {
                pixelNum = mapCoordToIndex(row + i, col + j);
                surroundingPixelArray[surroundingPixelArray.length] = pixelNum;
            }
        }
        return surroundingPixelArray;
    }

    function mapIndicestoValues(imageArray, indices) {
        var valueArray = [];
        for (var i = 0; i < indices.length; i++) {
            valueArray[i] = imageArray[indices[i]];
        }
        return valueArray;
    }

    function dotProduct(x, y) {
        var sum = 0;
        for (var i = 0; i < x.length; i++) {
            sum += x[i] * y[i];
        }
        return sum;
    }

    var filterNum = 0;
    var constraints = {audio: false, video: true}; 
    var video = document.getElementById('webcamVideo');

    navigator.mediaDevices.getUserMedia(constraints)
        .then(streamVideo)
        .catch(function(err) {
            console.log(err.name + ": " + err.message);
        }); // always check for errors at the end.

    // Initialize faces
    var faces = [];

    var webcamCanvas = document.getElementById('webcamCanvas');
    var webcamCtx = webcamCanvas.getContext('2d');
    var postDetectCanvas = document.getElementById('postDetectCanvas');
    var postDetectCtx = postDetectCanvas.getContext('2d');
    postDetectCanvas.style.transform = 'scale(1, 1)';

    var filterButtons = document.getElementsByClassName('filterButton');

    for (var i = 0; i < filterButtons.length; i++) {
        // Set a constant, otherwise the function gets written
        const filterNum = i;
        filterButtons[filterNum].onclick = function() {changeFilter(filterNum)};
    }

    grabFrameData();

})();
