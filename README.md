# object-detection

This repo illustrates how to use <a href="http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_tutorials.html">OpenCV</a> in a live application. Specifically, this provides examples of how to detect faces using <a href="https://en.wikipedia.org/wiki/Haar-like_features">Haar-like features</a> and pedestrians using the <a href="https://en.wikipedia.org/wiki/Histogram_of_oriented_gradients">Histogram of Oriented Gradients (HoG)</a>. There are three folders in this repo:

- XML_files: A folder containing XML files used for Haar cascades
- local_dev: A local Python implementation of the two aforementioned algorithms
- image_flask_app: A flask implementation of the face detection algorithm
