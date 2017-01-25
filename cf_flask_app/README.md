# cf_flask_app

This is a flask implementation of the face detection algorithm that can be pushed to Cloud Foundry. It achieves this by navigator.mediaDevices.getUserMedia() to stream webcam images from the browser. The images are then posted to Python, where we do the same processing. 
