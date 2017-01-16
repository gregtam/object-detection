#!/usr/bin/env python

"""
Face tracking with the option of loading a video or tracking live.
The options -r and -s change the resolution of the image to change
tracking capabilities and also change the output video resolution.
Only one of these options is allowed.

Options:
-r: resolution (The height of the resolution the video is changed to. Cannot be used with -s.)
-s: scale factor (The amount width and height are scaled by. Higher improves speed but is coarser. Default=1)
-w: webcam number (This specifies which webcam to use. Default=0)

--blur_face: Blur the face instead of drawing a box

Args:
Output video name (optional) - name of the output file
"""

from datetime import datetime
import getopt
import sys

import cv2
import numpy as np
from skimage.filters import gaussian

def get_command_line_arguments():
    """Imports the command-line arguments."""
    
    args = sys.argv[1:]
    optlist, args = getopt.getopt(args, 'r:s:w:', ['blur_face'])
    optdict = dict(optlist)

    return optdict, args

def add_blur_to_face(frame, coord):
    """Adds blur to frame based off of coordinates"""

    x, y, w, h = coord
    # Circular blur
    face_frame = frame[y:y+h, x:x+w]
    blur_img = gaussian(face_frame, 20) * 255

    # Mesh grids (accounts for even or odd width and height)
    y_f, x_f = np.ogrid[-h/2.0 + 0.5 : h/2.0 + 0.5,
                        -w/2.0 + 0.5 : w/2.0 + 0.5]

    # Draws an elliptical blur.
    # OpenCV seems to only return squares for where the
    # faces are (hence we will only ever use circles).
    # Nevertheless, we put the code in to deal with ellipses.
    mask = (x_f/(w/2.0))**2 + (y_f/(h/2.0))**2 <= 1
    face_frame[mask] = blur_img[mask]

    return frame

def find_faces(frame, min_size):
    """
    Takes in an Image, converts it to grayscale, then returns
    the location of potential faces.
    """

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(gray,
                                         scaleFactor=1.1,
                                         minNeighbors=5,
                                         # Minimum size set large enough to not 
                                         # capture random small squares
                                         minSize=min_size,
                                         flags=cv2.cv.CV_HAAR_SCALE_IMAGE
                                        )

    return faces

def get_new_shape(frame_width, frame_height, optdict, res_opt, scale_opt):
    """Get the new size of the video given options."""

    # Check for exceptions
    if res_opt and scale_opt:
        raise Exception('Options error: Cannot specify both -r and -s.')

    elif res_opt:
        try:
            resolution = int(optdict['-r'])
        except:
            raise Exception('Options Error: resolution must be an integer.\n')

    elif scale_opt:
        try:
            scale_factor = float(optdict['-s'])
        except:
            raise Exception('Options Error: scale_factor must be a number.\n')

    # Assign new shape
    if res_opt:
        new_shape = (int(frame_width/frame_height * resolution), resolution)
    elif scale_opt:
        new_shape = (int(round(frame_width/scale_factor)), int(round(frame_height/scale_factor)))
    else:  # If scale_factor isn't specified, set to 1
        new_shape = (int(frame_width), int(frame_height))

    return new_shape


optdict, args = get_command_line_arguments()

save_video = len(args) > 0
blur_face = '--blur_face' in optdict

if save_video:
    if len(args) > 1:
        raise Exception('Cannot specify more than one video name')
    else:
        file_name = args[0]

faceCascade = cv2.CascadeClassifier('../XML_files/haarcascade_frontalface_default.xml')

# Specify webcam number
if '-w' in optdict:
    try:
        webcam_nbr = int(optdict['-w'])
    except:
        raise Exception('Options Error: webcam_nbr must by an integer.')
    video_capture = cv2.VideoCapture(webcam_nbr)  # number indicates which webcam
# Otherwise, use webcam 0
else:
    video_capture = cv2.VideoCapture(0)

frame_width = video_capture.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
frame_height = video_capture.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)

res_opt = '-r' in optdict
scale_opt = '-s' in optdict

new_shape = get_new_shape(frame_width, frame_height, optdict, res_opt, scale_opt)


if save_video:
    all_frames = []
    frame_times = []

while True:
    if save_video:
        frame_start_time = datetime.now()
    # Capture frame-by-frame
    ret, frame = video_capture.read()
    frame = cv2.resize(frame, new_shape)
    faces = find_faces(frame, min_size=(new_shape[1]/5, new_shape[1]/5))

    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        if blur_face:
            frame = add_blur_to_face(frame, (x, y, w, h))
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
