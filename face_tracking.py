#!/Users/gregorytam/anaconda/bin/python

"""
Face tracking with the option of loading
a video or tracking live.

Options:
-w: webcam number (This specifies which webcam to use. Default=0)

Args:
Output video name - name of the output file
"""

from datetime import datetime
import getopt
import sys

import cv2
from skimage.filters import gaussian

# Import command-line arguments
args = sys.argv[1:]
optlist, args = getopt.getopt(args, 'w:')
optdict = dict(optlist)
save_video = len(args) > 0

if save_video:
    if len(args) > 1:
        raise Exception('Cannot specify more than one video name')
    file_name = args[0]

faceCascade = cv2.CascadeClassifier('XML_files/haarcascade_frontalface_default.xml')

# Specify webcam number
if '-w' in optdict:
    video_capture = cv2.VideoCapture(int(optdict['-w']))  # number indicates which webcam
else:
    video_capture = cv2.VideoCapture(0)

frame_width = video_capture.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
frame_height = video_capture.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)

scale_factor = 3
new_shape = (int(frame_width/scale_factor), int(frame_height/scale_factor))

if save_video:
    fourcc = cv2.cv.CV_FOURCC('m', 'p', '4', 'v')
    output_video = cv2.VideoWriter(file_name, fourcc, 8, new_shape)

while 1:
    # Capture frame-by-frame
    ret, frame = video_capture.read()
    frame = cv2.resize(frame, new_shape)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(gray,
                                         scaleFactor=1.1,
                                         minNeighbors=5,
                                         minSize=(30, 30),
                                         flags=cv2.cv.CV_HAAR_SCALE_IMAGE
                                        )

    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        # frame[y:y+h, x:x+w, :] = gaussian(frame[y:y+h, x:x+w], 15) * 255
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 2)

    if save_video:
        output_video.write(frame)

    # Display the resulting frame (mirrored)
    cv2.imshow('Video', cv2.flip(frame, 1))

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()
