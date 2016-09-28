#!/Users/gregorytam/anaconda/bin/python

"""
Face tracking with the option of loading
a video or tracking live.

Options:
-s: scale factor (The amount width and height are scaled by. Higher improves speed but is coarser.)
-w: webcam number (This specifies which webcam to use. Default=0)

Args:
Output video name (optional) - name of the output file
"""

from datetime import datetime
import getopt
import sys

import cv2
import numpy as np
from skimage.filters import gaussian

# Import command-line arguments
args = sys.argv[1:]
optlist, args = getopt.getopt(args, 's:w:', ['blur_face'])
optdict = dict(optlist)
save_video = len(args) > 0
blur_face = '--blur_face' in optdict

if save_video:
    if len(args) > 1:
        raise Exception('Cannot specify more than one video name')
    file_name = args[0]

faceCascade = cv2.CascadeClassifier('XML_files/haarcascade_frontalface_default.xml')

# Specify webcam number
if '-w' in optdict:
    video_capture = cv2.VideoCapture(int(optdict['-w']))  # number indicates which webcam
# Otherwise, use webcam 0
else:
    video_capture = cv2.VideoCapture(0)

frame_width = video_capture.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
frame_height = video_capture.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)

if '-s' in optdict:
    scale_factor = float(optdict['-s'])
else:
    scale_factor = 1
new_shape = (int(round(frame_width/scale_factor)), int(round(frame_height/scale_factor)))

if save_video:
    all_frames = []
    frame_times = []

while 1:
    if save_video:
        frame_start_time = datetime.now()
    # Capture frame-by-frame
    ret, frame = video_capture.read()
    frame = cv2.resize(frame, new_shape)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(gray,
                                         scaleFactor=1.1,
                                         minNeighbors=5,
                                         # Minimum size set large enough to capture random
                                         # small squares
                                         minSize=(new_shape[1]/5, new_shape[1]/5),
                                         flags=cv2.cv.CV_HAAR_SCALE_IMAGE
                                        )

    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        if blur_face:
            frame[y:y+h, x:x+w, :] = gaussian(frame[y:y+h, x:x+w], 15, multichannel=False) * 255
        else:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 2)

    if save_video:
        # Add frames to a list, so we can save them later
        all_frames.append(frame)

    # Display the resulting frame (mirrored)
    cv2.imshow('Video', cv2.flip(frame, 1))

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Compute the time to process the frame and add to array
    if save_video:
        frame_times.append((datetime.now() - frame_start_time).total_seconds())

if save_video:
    print '\nSaving video...'
    start = datetime.now()
    fourcc = cv2.cv.CV_FOURCC(*list('mp4v'))

    # Save video with the proper frame rate.
    # We do this because the frames might 
    # be processed slower depending on scale_factor.
    output_video = cv2.VideoWriter(file_name, fourcc, fps=round(1/np.mean(frame_times)), frameSize=new_shape)
    for frame in all_frames:
        output_video.write(frame)
    print 'Done saving video (in {})\n'.format(datetime.now() - start)


# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()
