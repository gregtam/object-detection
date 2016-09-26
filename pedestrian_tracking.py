#!/Users/gregorytam/anaconda/bin/python

"""
Load all frames ahead of time and then
analyze them.

Options:
-s: scale factor (The amount width and height are scaled by. Higher improves speed but is coarser.)
-t: sleep time (The amount of time to wait between displaying frames. This is 1/frame_rate. Default=33)
--use_webcam: Use webcam instead of loading from a video. This is not live since pedestrian detection is slow.
              Instead, it will capture the video first, then do detection afterwards
--save_as: Output video name

Args:
Input video name - name of the file to input
"""

from datetime import datetime
import getopt
import sys

import cv2
import numpy as np

# Import command-line arguments
args = sys.argv[1:]
optlist, args = getopt.getopt(args, 's:t:', ['use_webcam', 'save_as='])
optdict = dict(optlist)

save_video = '--save_as' in optdict
if save_video:
    file_name = optdict['--save_as']

# Select video (webcam or file)
use_webcam = '--use_webcam' in optdict
start = datetime.now()
if use_webcam and len(args) > 0:
    raise Exception('use_webcam cannot be used with a file. Specify one or the other.')
if use_webcam:
    cap = cv2.VideoCapture(1)  # number indicates which webcam
else:
    cap = cv2.VideoCapture(args[0])

frame_num = 0

# Load frames from video
print '\nLoading video...'

ret = True
all_frames = []
all_small_frames = []
# Amount to scale image down to find pedestrians.
# Higher means faster, but it will be coarser.
if '-s' in optdict:
    try:
        scale_factor = float(optdict['-s'])
    except:
        print 'Options Error: scale_factor must be a float\n'
else:  # default scale factor
    scale_factor = 1

# Sleep time between frames (affects frame rate)
if '-t' in optdict:
    try:
        sleep_time = int(optdict['-t'])
    except:
        print 'Options Error: sleep_time must be an integer\n'
elif use_webcam:  # default sleep time for webcam recording
    sleep_time = 8
else:  # default sleep time for videos
    sleep_time = 33


frame_width = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))
new_shape = (int(frame_width/scale_factor), int(frame_height/scale_factor))


if save_video:
    fourcc = cv2.cv.CV_FOURCC('m', 'p', '4', 'v')
    output_video = cv2.VideoWriter(file_name, fourcc, 30, (frame_width, frame_height))

while ret:
    ret, frame = cap.read()
    if ret:
        all_frames.append(frame)
        frame_width = cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
        frame_height = cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)

        if use_webcam:
            cv2.imshow('Recording', cv2.resize(frame, (int(frame_width/2), int(frame_height/2))))
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        new_shape = (int(frame_width/scale_factor), int(frame_height/scale_factor))
        # Change size of image
        all_small_frames.append(cv2.resize(frame, new_shape))
print 'Done loading video (in {})'.format(datetime.now() - start)

cap.release()
cv2.destroyAllWindows()


# Initialize values
first_frame = True
hog_detector = cv2.HOGDescriptor()  # establish detector
hog_detector.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())


# Detect pedestrians
print '\nDetecting pedestrians'
start = datetime.now()
for frame_num in range(0, len(all_small_frames)):
    gray = cv2.cvtColor(all_small_frames[frame_num], cv2.COLOR_BGR2GRAY)

    if first_frame or len(rects) == 0:
        (rects, weights) = hog_detector.detectMultiScale(gray, winStride=(4, 4), padding=(8, 8), scale=1.05)
        if len(rects) > 0:
            # Pick best rectangle
            best_index = np.argmax(weights)
            best_rect = rects[best_index]
        first_frame = False
    else:
        temp_rects = []  # temporary rects, so we can overwrite rects later
        # Amount of area to search for a new pedestrian
        padding_amt = 20
        if best_rect[0] - padding_amt < 0:
            x1 = 0
        else:
            x1 = best_rect[0] - padding_amt

        if best_rect[0] + best_rect[2] + padding_amt > gray.shape[1]:
            x2 = all_small_frames[frame_num].shape[1]
        else:
            x2 = best_rect[0] + best_rect[2] + padding_amt

        if best_rect[1] - padding_amt < 0:
            y1 = 0
        else:
            y1 = best_rect[1] - padding_amt

        if best_rect[1] + best_rect[3] + padding_amt > gray.shape[0]:
            y2 = all_small_frames[frame_num].shape[0]
        else:
            y2 = best_rect[1] + best_rect[3] + padding_amt

        sub_frame = gray[y1:y2, x1:x2]

        (rects, weights) = hog_detector.detectMultiScale(sub_frame, winStride=(4, 4), padding=(8, 8), scale=1.05)
        if len(rects) > 0:
            # Pick best sub-rectangle
            best_index = np.argmax(weights)
            best_rect = rects[best_index] + [x1, y1, 0, 0]

    if len(rects) > 0:
        rect_x, rect_y = tuple([int(i) for i in best_rect[:2] * scale_factor])
        rect_w, rect_h = tuple([int(i) for i in (best_rect[:2] + best_rect[2:]) * scale_factor])
        cv2.rectangle(all_frames[frame_num],
                      (rect_x, rect_y),
                      (rect_w, rect_h),
                      (255, 255, 255), 
                      2)

print 'Done detecting pedestrians (in {})\n'.format(datetime.now() - start)

if save_video:
    print 'Saving video...'
for frame_num in range(len(all_frames)):
    if save_video:
        if use_webcam:  # display smaller image if using webcam
            cv2.resize(all_frames[frame_num], new_shape)
        output_video.write(all_frames[frame_num])
    else:
        if use_webcam:  # display smaller image if using webcam
            cv2.resize(all_frames[frame_num], new_shape)
        cv2.imshow('Frame', all_frames[frame_num])


    if cv2.waitKey(sleep_time) & 0xFF == ord('q'):
        break
    frame_num += 1

if save_video:
    print 'Video saved as {}\n'.format(file_name)

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()