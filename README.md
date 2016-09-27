# Image-Detection

A few files showing OpenCV used in a live application. 

face_tracking.py: Uses haar-like features to find a face using a webcam. It then draws a box around the faces found in real time.

XML_files: A folder containing the XML files used for haar cascades.

pedestrian_tracking.py: Given a video, this file uses the Histogram of Oriented Gradients (HoG) method to find a pedestrian and draws a box around it. There are some other subtleties to speed up this process such as searching in a narrower range.

walking2.mp4: Sample walking video.

walking2_small.mp4: A smaller resolution version of walking2.mp4. This allows for faster computation.

youtube_pedestrian_tracking.py: Does the same thing as pedestrian_tracking.py, but instead of loading in a local file, it takes in a YouTube ID and does analysis on that.
