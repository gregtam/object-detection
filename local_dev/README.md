# local_dev

This folder contains few files showing <a href="http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_tutorials.html">OpenCV</a> used in a live local Python application. 

## face_tracking.py
Uses <a href="https://en.wikipedia.org/wiki/Haar-like_features">Haar-like features</a> to find a face using a webcam. It then draws a box around the faces found in real time.

To use this, we either run `python face_tracking.py` or `./face_tracking.py`. The latter option only works if the Python file is executable. We can achieve this by running `chmod 700 face_tracking.py` or `chmod u+x face_tracking.py`. We can also specify options to this.

First, we can specify either the `-r` or `-s` options along with a number to change the resolution  or scale the video dimensions respectively. The number after the `-r` option represents the height of the desired video in pixels. The width will be determined by keeping the video proportions the same. The `-s` scales width and height down by the given number. For example, if we scale by 2, it will shrink both the height and width by 2. The higher the scale factor, the quicker the algorithm will run since the detection is being performed on smaller images. However, performance will be decreased.
```
./face_tracking.py -r 1000
./face_tracking.py -s 2
```

## pedestrian_tracking.py
Given a video, this file uses the <a href="https://en.wikipedia.org/wiki/Histogram_of_oriented_gradients">Histogram of Oriented Gradients (HoG)</a> method to find a pedestrian and draws a box around it. There are some other subtleties to speed up this process such as searching in a narrower range.

This file uses the same `-s` and `-w` options, but additionally adds some options. First, we may specify ``--use_webcam`` to record from the webcam first, instead of taking from an input video file. To save as a file, we use the ``--save_as`` option with with the file name. Finally, the `-t` option with an integer number indicates the delay between frames in the output video. We can run the following code to detect the pedestrian, then save it to a file.
```
./pedestrian_tracking.py --save_as=walking_sample_tracked.mp4 walking_sample.mp4
```

The `-w` option specifies which webcam should be used. By default it is set to 0 (assuming only one webcam).

If the `--blur_face` option is present, then it will blur the face it finds instead of the default setting, which is to draw a box around the face.

We may also specify a video name at the end. In this case, the program will output the video to a file. To exit out of the video so that it saves, we can press the `q` key while the video is recording.

## youtube_pedestrian_tracking.py
This achieves the same thing as pedestrian_tracking.py, but instead of loading a local file, it takes a YouTube ID as an option, loads the video, then does analysis on that.

## Files
- walking_sample.mp4: Sample walking video.

- walking_sample_tracked.mp4: A video containing the tracked results of the walking sample video.
