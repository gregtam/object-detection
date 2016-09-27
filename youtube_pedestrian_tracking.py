#!/Users/gregorytam/anaconda/bin/python

# TODO: stabilize rectangle - write code to limit amount rectangle size can change.

"""
Load all frames ahead of time and then
analyze them.

Options:
-s: scale factor (The amount width and height are scaled by. Higher improves speed but is coarser.)
-t: sleep time (The amount of time to wait between displaying frames. This is 1/frame_rate. Default=33)
-k: keep video (If tag is present, then the original YouTube video will not be deleted.)
--save_as: If present, then it saves the video. This tag specifies output video name.
--input_link: Unique youtube id code of video we wish to download.
"""

from __future__ import unicode_literals  # used to properly download the youtube video
from datetime import datetime
import getopt  # module for switch options
import os
import subprocess  # used to access command line via Python
import sys

import cv2
import pandas as pd
import numpy as np
import youtube_dl

# Import command-line arguments
args = sys.argv[1:]
optlist, args = getopt.getopt(args, 'ks:t:', ['resolution=', 'save_as='])
optdict = dict(optlist)

save_video = '--save_as' in optdict
if save_video:
    file_name = optdict['--save_as']

if len(args) == 1:
    youtube_id = args[0]

    choose_res = '--resolution' in optdict
    if choose_res:
        res = int(optdict['--resolution'])
        # Get the youtube video's available resolutions.
        # This works by sending a terminal command and retrieving the results
        cmd = 'youtube-dl -F {id}'.format(id=youtube_id).split()
        output = subprocess.Popen( cmd, stdout=subprocess.PIPE ).communicate()[0]
        output = output.strip('\n')

        # Split the output lines up
        output_lines = np.array(output.split('\n'))
        # Starting point of the resolution
        res_index = int(np.where(output_lines == 'format code  extension  resolution note')[0])
        # Select only lines corresponding to resolution information
        output_lines = output_lines[res_index + 1:]

        # Create a table with the resolution information
        fmt_list = []
        code_list = []
        ext_list = []
        for i in range(len(output_lines)):
            temp_format, temp_code, temp_ext = output_lines[i].split()[:3]
            fmt_list.append(temp_format)
            code_list.append(temp_code)
            ext_list.append(temp_ext)
            
        df = pd.DataFrame()
        df['fmt'] = [int(i) for i in fmt_list]
        df['code'] = code_list
        df['ext'] = ext_list

        # Exclude audio files
        df = df[df.ext != 'audio'].reset_index(drop=True)
        # Only include mp4 files
        df = df[df.code == 'mp4'].reset_index(drop=True)
        # Split the resolution into corresponding width and height
        # columns, then convert to int
        df['width'], df['height'] = zip(*df['ext'].map(lambda res: [int(i) for i in res.split('x')]))

        if res in df['height'].tolist():
            temp_df = df[df.height == res].reset_index(drop=True)  # select rows with the resolution
            format_id = temp_df.fmt[0]
        else:
            raise Exception('This resolution is not available for this YouTube video.')

        ydl_opts = {'outtmpl': '{path}/temp_youtube_vid_{id}.mp4'.format(path=os.getcwd(), id=youtube_id),
                    'format': str(format_id)}
    else:
        ydl_opts = {'outtmpl': '{path}/temp_youtube_vid_{id}.mp4'.format(path=os.getcwd(), id=youtube_id)}

    # If file already exists, remove it
    if 'temp_youtube_vid_{id}.mp4'.format(id=youtube_id) in os.listdir('.'):
        os.remove('temp_youtube_vid_{id}.mp4'.format(id=youtube_id))

    # Download the YouTube video locally
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(['https://www.youtube.com/watch?v={id}'.format(id=youtube_id)])
elif len(args) == 0:
    raise Exception('Must specify a YouTube ID')
else:
    raise Exception('Must specify only one YouTube ID')


start = datetime.now()
cap = cv2.VideoCapture('temp_youtube_vid_{id}.mp4'.format(id=youtube_id))

frame_num = 0

print '\nLoading video...'
# skip first 32 frames
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

if '-t' in optdict:
    try:
        sleep_time = int(optdict['-t'])
    except:
        print 'Options Error: sleep_time must be an integer\n'
else:  # default sleep time
    sleep_time = 33

frame_width = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))

new_shape = (int(frame_width/scale_factor), int(frame_height/scale_factor))


if save_video:
    fourcc = cv2.cv.CV_FOURCC(str('m'), str('p'), str('4'), str('v'))
    output_video = cv2.VideoWriter(file_name, fourcc, 30, (frame_width, frame_height))

while ret:
    ret, frame = cap.read()
    if ret:
        all_frames.append(frame)
        frame_width = cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
        frame_height = cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)

        new_shape = (int(frame_width/scale_factor), int(frame_height/scale_factor))
        # Change shape of image
        # new_shape = tuple([int(i/scale_factor) for i in frame.shape[1::-1]])
        all_small_frames.append(cv2.resize(frame, new_shape))
print 'Done loading video (in {})'.format(datetime.now() - start)

# Initialize values
first_frame = True

hog_detector = cv2.HOGDescriptor()
hog_detector.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())


print '\nDetecting pedestrians...'
start = datetime.now()
for frame_num in range(len(all_small_frames)):
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
        padding_amt = 10
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

            # ALl rectangles
            # for rect in rects:
            #   rect += [x1, y1, 0, 0]


    if len(rects) > 0:
        # Best rectangle
        rect_x, rect_y = tuple([int(i) for i in best_rect[:2] * scale_factor])
        rect_x2, rect_y2 = tuple([int(i) for i in (best_rect[:2] + best_rect[2:]) * scale_factor])
        cv2.rectangle(all_frames[frame_num],
                      (rect_x, rect_y),
                      (rect_x2, rect_y2),
                      (255, 255, 255), 
                      2)

        # All rectangles
        # for rect in rects:
        #   rect_x, rect_y = tuple([int(i) for i in rect[:2] * scale_factor])
        #   rect_x2, rect_y2 = tuple([int(i) for i in (rect[:2] + rect[2:]) * scale_factor])
        #   cv2.rectangle(all_frames[frame_num],
        #                 (rect_x, rect_y),
        #                 (rect_x2, rect_y2),
        #                 (255, 255, 255),
        #                 2)
    # Put frame number on image
    cv2.putText(all_frames[frame_num], 'Frame {}'.format(frame_num), (25, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)

print 'Done detecting pedestrians (in {})\n'.format(datetime.now() - start)

print 'Saving video...'
start = datetime.now()
for frame_num in range(len(all_frames)):
    if save_video:
        output_video.write(all_frames[frame_num])
    else:
        cv2.imshow('Frame', all_frames[frame_num])

    if cv2.waitKey(sleep_time) & 0xFF == ord('q'):
        break
    frame_num += 1

# Remove video
if not '-k' in optdict and 'temp_youtube_vid.mp4' in os.listdir('.'):
    os.remove('temp_youtube_vid.mp4')

# Save video file
if save_video:
    print 'Video saved as {} (in {})\n'.format(file_name, datetime.now() - start)

# When everything is done, release the capture
cap.release()
cv2.destroyAllWindows()