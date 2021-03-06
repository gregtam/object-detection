function streamVideo(mediaStream) {
  video.srcObject = mediaStream;
  video.onloadedmetadata = function(e) {
    video.play();
  }
}

function drawFilter() {
  var imageData = webcamCtx.getImageData(0, 0,
                                         webcamCanvas.width,
                                         webcamCanvas.height);
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
    for (var j = 0; j < imageData.data.length; j++) {
      var coordinates = mapIndexToCoord(j);
      var row = coordinates[0];
      var col = coordinates[1];

      if ((col >= faceX) && (col <= faceX + faceW)
          && (row >= faceY) && (row <= faceY + faceH)) {
        if (j % 4 < 3) {
          if (filterNum == 0) {
            pixelCopy[j] = 255 - imageData.data[j];
          }
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
    // Draw three lines so that it appears thicker
    for (var i = 0; i < 8; i++) {
      postDetectCtx.strokeRect(faceX + i, faceY + i,
                               faceW - 2*i, faceH - 2*i);
    }
  }
}

function changeFilter(num) {
  if (num < 4) {
    filterNum = num;
    
    filterButtons[num].style.background = '#008774';
    for (var i = 0; i < 4; i++) {
      if (i != num) {
        filterButtons[i].style.background = '#00AE9E';
      }
    }
  }
}

function toggleMirror() {
  // Toggle mirror
  if (postDetectCanvas.style.transform == 'scale(-1, 1)')
    postDetectCanvas.style.transform = 'scale(1, 1)';
  else if (postDetectCanvas.style.transform == 'scale(1, 1)')
    postDetectCanvas.style.transform = 'scale(-1, 1)';
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
  });

// Initialize faces
var faces = [];

// Get the post processing canvas, where we mark where the face is
var postDetectCanvas = document.getElementById('postDetectCanvas');
var postDetectCtx = postDetectCanvas.getContext('2d');

// Set transform ahead of time so we have the option to mirror it later
postDetectCanvas.style.transform = 'scale(1, 1)';

// Get the webcam canvas, which is where the webcam image is pasted on
var webcamCanvas = document.getElementById('webcamCanvas');
var webcamCtx = webcamCanvas.getContext('2d');

var filterButtons = document.getElementsByClassName('btn');
// Initialize first filterButton
filterButtons[0].style.background = '#008774';
for (var i = 0; i < 4; i++) {
  // Set a constant, otherwise the the loop will not properly cycle through all
  // of the buttons
  const filterNum = i;
  filterButtons[filterNum].onclick = function() {
    changeFilter(filterNum);
    console.log(filterNum);
  };
}

var toggleMirrorButton = document.getElementById('toggleMirrorButton');
toggleMirrorButton.onclick = function() {
  toggleMirror();
};
toggleMirrorButton.onmousedown = function() {
  toggleMirrorButton.style.backgroundColor = '#008774';
}
toggleMirrorButton.onmouseup = function() {
  toggleMirrorButton.style.backgroundColor = '#00AE9E';
}

var captureButton = document.getElementById('captureButton');
captureButton.onmousedown = function() {
  // Change colour when button gets pressed
  // captureButton.style.backgroundColor = '#008774';
  captureButton.style.backgroundColor = '#444444';
};
captureButton.onmouseup = function() {
  // Change colour when button is released, grab the frame, then detect faces
  // and draw the filter.

  // We use a promise to separate frame grabbing and drawing the filter
  // because they are asynchronous processes and a new frame will be created
  // by the time the face is detected. We need to grab the frame, wait until
  // that finishes, then draw the filter.

  console.log(filterNum);
  captureButton.style.backgroundColor = 'black';
  var grabFramePromise = new Promise((resolve, reject) => {
    function postImage(imageData) {
      // Post Image Data to Flask
      var postReq = new XMLHttpRequest();
      postReq.open('POST', '/detect_faces', true);
      postReq.responseType = 'json';

      postReq.onload = function(event) {
        if (this.readyState == 4 && this.status == 200) {
          faces = postReq.response.faces;
          // Waits until frame is loaded before running drawFilter(). This
          // prevents the another frame from being shown while detecting the
          // faces from the previous frame.
          resolve('Grabbed data');
        }
      }

      postReq.send(imageData);
    }

    function grabFrameData() {
      // Draws the video image onto canvas with id = webcamCanvas
      webcamCtx.drawImage(video, 0, 0,
                          webcamCanvas.width, webcamCanvas.height);
      // Posts the webcamCanvas image to the detect_faces() function
      webcamCanvas.toBlob(postImage, 'image/jpeg', 1);
    }

    grabFrameData();
  });

  grabFramePromise.then((successMessage) => {
    // Draws the filter after grabbing the frame
    drawFilter();
  })
};
