#!/usr/bin/env python

from datetime import datetime
from flask import Flask, render_template, request, Response
import getopt
import os
import sys

import cv2
import numpy as np
import pandas as pd
from PIL import Image

app = Flask(__name__)

def get_command_line_arguments():
    args = sys.argv[1:]
    optlist, args = getopt.getopt(args, 'w:')
    optdict = dict(optlist)

    return optdict, args

def capture_webcam_img(video_capture, webcam_nbr=0):
    """
    Captures an image form the specified webcam and returns the image
    as a numpy array.

    Inputs:
    webcam_nbr - An integer value specifying the webcam number (Default: 0)
    """

    start = datetime.now()
    # Capture image from webcam
    ret, frame = video_capture.read()
    if debug:
        print '        Read image: {}'.format(datetime.now() - start)

    if not ret:
        raise Exception('Did not read in webcam')

    start = datetime.now()
    frame_width = video_capture.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
    frame_height = video_capture.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)

    scale_factor = 5
    new_shape = (int(frame_width/scale_factor), int(frame_height/scale_factor))
    frame = cv2.resize(frame, new_shape)

    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    if debug:
        print '        Scale Image: {}'.format(datetime.now() - start)

    return ret, img

def get_face_img(video_capture, filter_type=0, webcam_nbr=0):
    """
    Captures image from Webcam then runs Viola-Jones algorithm
    to find face in image.
    """

    def _find_faces(face_cascade, frame, min_size):
        """
        Takes in an Image, converts it to grayscale, then returns
        the location of potential faces.
        """

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray,
                                              scaleFactor=1.1,
                                              minNeighbors=5,
                                              # Minimum size set large enough to not 
                                              # capture random small squares
                                              minSize=min_size,
                                              flags=cv2.cv.CV_HAAR_SCALE_IMAGE
                                             )

        return faces

    def _add_blur_to_face(frame, coord):
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

    face_cascade = cv2.CascadeClassifier('../XML_files/haarcascade_frontalface_default.xml')

    start = datetime.now()
    ret, frame = capture_webcam_img(video_capture, webcam_nbr)
    if debug:
        print '    Capture Image: {}'.format(datetime.now() - start)
   
    start = datetime.now()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    if debug:
        print '    Change to RGB: {}'.format(datetime.now() - start)

    start = datetime.now()
    faces = _find_faces(face_cascade, frame, (int(frame.shape[0]/4), int(frame.shape[0]/4)))
    if debug:
        print '    Find Faces: {}'.format(datetime.now() - start)

    start = datetime.now()
    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        if filter_type == 0:
            # Add box around face
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 2)
        elif filter_type == 1:
            # Blur face
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 2)
    if debug:
        print '    Draw Rectangles: {}'.format(datetime.now() - start)

    # Flip frame horizontally (mirror)
    flipped_frame = cv2.flip(frame, 1)
    return flipped_frame

def generate_face_img(video_capture, filter_type):
    while True:
        start = datetime.now()
        frame = get_face_img(video_capture, filter_type)
        if debug:
            print 'Get Faces: {}'.format(datetime.now() - start)

        start = datetime.now()
        ret, jpeg_frame = cv2.imencode('.jpg', frame)
        if debug:
            print 'Encode to JPEG: {}'.format(datetime.now() - start)
            print
        if ret:
            yield (b'--frame\n'
                   b'Content/Type: image/jpeg\n\n' + jpeg_frame.tobytes() + b'\n')

@app.route('/')
def index():
    html = render_template('index.html')
    return html

@app.route('/video_feed/<filter_type>')
def video_feed(filter_type):
    """Stream images"""

    optdict, args = get_command_line_arguments()
    if '-w' in optdict:
        webcam_nbr = optdict['-w']
    else:
        webcam_nbr = 0

    if debug:
        print 'webcam number', webcam_nbr

    start = datetime.now()
    # print 'file: ', url_for('static', filename='walking_sample.mp4')
    # video_capture = cv2.VideoCapture('static/walking_sample.mp4')
    video_capture = cv2.VideoCapture(0)
    if debug:
        print '        cv2.VideoCapture: {}'.format(datetime.now() - start)

    return Response(generate_face_img(video_capture, int(filter_type)), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    debug = False
    app.run()
