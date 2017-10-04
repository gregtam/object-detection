# object-detection

This repo illustrates how to use [OpenCV](http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_tutorials.html) in a live application. Specifically, this provides examples of how to detect faces using [Haar-like features](https://en.wikipedia.org/wiki/Haar-like_features) and pedestrians using the [Histogram of Oriented Gradients (HoG)](https://en.wikipedia.org/wiki/Histogram_of_oriented_gradients). There are four folders in this repo:

- XML_files: A folder containing XML files used for Haar cascades
- local_dev: A local Python implementation of the two aforementioned algorithms
- local_flask_app: A local flask implementation of the face detection algorithm
- cf_flask_app: A flask implementation of the face detection algorithm that can be pushed to Cloud Foundry

View the final application [here](https://face-detection.cfapps.pez.pivotal.io/).
