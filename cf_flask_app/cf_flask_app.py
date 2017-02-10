#!/usr/bin/env python

import cPickle
from StringIO import StringIO
import os

import cv2
from flask import Flask, jsonify, render_template, request, url_for
import numpy as np
from PIL import Image

app = Flask(__name__)

# face_cascade = cv2.CascadeClassifier('../XML_files/haarcascade_frontalface_default.xml')


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
    return render_template('index.html')

@app.route('/detect_faces', methods=['POST'])
def detect_faces():
    if request.method == 'POST':
        img = Image.open(StringIO(request.data))
        frame = np.array(img)


        # # Works, No flickering
        # f = open('equal.txt', 'r')
        # frame = cPickle.load(f)

        # f = open('frame.txt', 'w')
        # cPickle.dump(frame, f)

        # f = open('frame.txt', 'r')
        # frame_2 = cPickle.load(f)

        # equal_images = np.all(frame == frame_2)
        # print equal_images

        # if equal_images:
        #     img.save('equal.png')
        #     f = open('equal.txt', 'w')
        #     cPickle.dump(np.asarray(img), f)
        # else:
        #     img.save('different.png')
        #     f = open('different.txt', 'w')
        #     cPickle.dump(np.asarray(img), f)

        # print "{} ---- {}".format(np.sum(frame), np.sum(frame_2))
        # print

        face_cascade = cv2.CascadeClassifier('../XML_files/haarcascade_frontalface_default.xml')
        faces = find_faces(face_cascade, frame, (int(frame.shape[0]/4), int(frame.shape[0]/4)))

        if len(faces) > 0:
            return jsonify(faces=faces)
        else:
            return jsonify(faces=[])

if __name__ == "__main__":
    app.run(debug=True)
