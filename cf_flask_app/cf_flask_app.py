#!/usr/bin/env python
# gunicorn -w 4 -b 127.0.0.1:5000 cf_flask_app:app

import cPickle
from StringIO import StringIO
import os

import cv2
from flask import Flask, jsonify, render_template, request, url_for
import numpy as np
from PIL import Image

app = Flask(__name__)

face_cascade = cv2.CascadeClassifier('../XML_files/haarcascade_frontalface_default.xml')

def find_faces(face_cascade, frame, min_size):
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

    if len(faces) > 0:
        return faces.tolist()
    else:
        return []

@app.route('/')
def index():
    return render_template('layout.html', page_name='index')

@app.route('/about')
def about_page():
    return render_template('layout.html', page_name='about')

@app.route('/detect_faces', methods=['POST'])
def detect_faces():
    if request.method == 'POST':
        img = Image.open(StringIO(request.data))
        frame = np.array(img)

        faces = find_faces(face_cascade, frame, (int(frame.shape[0]/4), int(frame.shape[0]/4)))

        if len(faces) > 0:
            return jsonify(faces=faces)
        else:
            return jsonify(faces=[])

if __name__ == "__main__":
    app.run(debug=True)
