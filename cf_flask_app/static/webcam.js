(function() {

    var constraints = {audio: false, video: true}; 
    var video = document.getElementById('webcamVideo');
    // var video = document.querySelector('video');

    function streamVideo(mediaStream) {
        video.srcObject = mediaStream;
        video.onloadedmetadata = function(e) {
            video.play();
        }
    }

    navigator.mediaDevices.getUserMedia(constraints)
        .then(streamVideo)
        .catch(function(err) {console.log(err.name + ": " + err.message);}); // always check for errors at the end.

    var canvas = document.getElementById('webcamCanvas');
    var ctx = canvas.getContext('2d');
    var faces = [[248, 195, 143, 143]];

    // Testing with a fixed image
    var faceImg = document.querySelector('img');
    console.log('HERE ' + faceImg);

    function waitForFrame() {
        window.setTimeout(function() {
            grabFrameData();
        }, 2000);
    }
    waitForFrame();

    // function grabFrameData() {
    //     var delay = 500;
    //     console.log('Start Time: ' + new Date().getTime());
    //     window.setTimeout(function() {canvas.toBlob(postImage, 'image/jpeg', 1);}, delay);
    //     console.log('Get Faces: ' + new Date().getTime());
    //     window.setTimeout(function() {ctx.drawImage(video, 0, 0, canvas.width, canvas.height);}, delay);
    //     console.log('Draw Webcam: ' + new Date().getTime());

    //     window.setTimeout(function() {
    //         console.log(faces);
    //         for (var i = 0; i < faces.length; i++) {
    //             var face = faces[i];
    //             console.log('HERE ' + faces);
    //             ctx.fillRect(face[0], face[1], face[2], face[3]);
    //         };
    //     }, delay);
    //     console.log('Filled Faces: ' + new Date().getTime());

    //     window.setTimeout(function() {
    //         waitForFrame();
    //     }, 1000);
    // }

    function grabFrameData() {
        // console.log('Start Time: ' + new Date().getTime());
        canvas.toBlob(postImage, 'image/jpeg', 1);
        // console.log('Get Faces: ' + new Date().getTime());

        console.log('faceImg: ' + faceImg);
        ctx.drawImage(faceImg, 0, 0, canvas.width, canvas.height);
        // ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        // console.log('Draw Webcam: ' + new Date().getTime());

        // ctx.fillRect(0, 0, 100, 100);
        ctx.font = '36px serif';
        ctx.fillText(faces + '   ' + faces.length, 0, 140);

        for (var i = 0; i < faces.length; i++) {
            var face = faces[i];
            // console.log(faces[0]);
            // ctx.fillRect(0, 0, 100, 100);
            ctx.fillRect(face[0], face[1], face[2], face[3]);
        };
        // console.log('Filled Faces: ' + new Date().getTime());

        waitForFrame();
    }

    function postImage(imageData) {
        // Post Image Data to Flask
        var postReq = new XMLHttpRequest();
        postReq.open('POST', '/detect_faces', true);
        postReq.responseType = 'json';

        postReq.onload = function(event) {
            faces = postReq.response.faces;
            console.log("HERE " + faces);
            // faces = [1,2,3];
            // console.log('HERE ' + faces);
            // console.log('Faces');
            // console.log(faces);
            // console.log(faces.length);
            // for (var i = 0; i < faces.length; i++) {
            //     var face = faces[i];
            //     // console.log(faces[0]);
            //     ctx.fillRect(face[0], face[1], face[2], face[3]);
            // };
        }


        // console.log('HERE ' + faces);
        

        postReq.send(imageData);
    }



    //Old stuff


    // imageData = ctx.getImageData(0, 0, 200, 200);
    // for (i = 0; i < imageData.data.length; i++) {
    //     if (i % 4 != 3)
    //         imageData.data[i] = 0;
    //     else
    //         imageData.data[i] = 255;
    // }
    // console.log('imageData');
    // console.log(imageData.data);
    // ctx.putImageData(imageData, 10, 10);


    // //button
    // document.getElementById('snapshot').onclick = function() {
    //     var video = document.getElementById('webcamVideo');
    //     var canvas = document.getElementById('webcamCanvas');
    //     var ctx = canvas.getContext('2d');
    //     ctx.drawImage(video, 0, 0);

    //     console.log(ctx.getImageData(0, 0, canvas.width, canvas.height).data);
    //     console.log(ctx.getImageData(0, 0, 200, 200).data);

    //     var data = ctx.getImageData(0,0,canvas.width,canvas.height);
    //     console.log('Data Here');
    //     console.log(data.data);
    //     console.log(data.data[0]);
    //     //invert each pixel
    //     for(n=0; n<data.width*data.height; n++) {  
    //         var index = n*4;   
    //         data.data[index+0] = 255-data.data[index+0];  
    //         data.data[index+1] = 255-data.data[index+1];  
    //         data.data[index+2] = 255-data.data[index+2];  
    //         //don't touch the alpha  
    //     }
    //     console.log(data.data);
    //     console.log(data.data[0]);
          
    //     //set the data back  
    //     ctx.putImageData(data,0,0);     
    // }
})()

