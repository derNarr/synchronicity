#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# video.py

"""
Based on tutorials from
http://www.neuroforge.co.uk/index.php/input-and-output-with-open-cv

This module uses the python-opencv interface called cv. This is the old one.
The new one is cv2.

cv2 is more pythonic and does everything in numpy.

see
http://stackoverflow.com/questions/10417108/what-is-different-between-all-these-opencv-python-interfaces/

In the end convert the outputvideo with:

    mencoder in.avi -o out.mpeg -ovc lavc -lavcopts vcodec=mpeg4:vbitrate=2400

    mencoder in.avi -o out.avi -ovc x264

"""

from __future__ import division

#import os
import time
import pickle

import cv
from scipy.misc import imsave
import numpy as np

VIDEO_FILE = "../videos/ducks_boat.mpeg"
DATA_PICKLE = "./ducks_boat_20.pickle"

FRAME_GAME_START = 0
FRAME_LENGTH_MS = 33.3333
OUT_FPS = 30
T_START = 0 # usec
T_STOP = 19*1000*1000 # usec
N_SHIFT = 1000 # in 10 msec


class GazeTrack(object):
    """
    loads video and ganze data and shows a gaze replay.

    """

    def __init__(self):
        """
        Load the data and store it in the class. Create windows, track bars,
        and video capture.

        """
        self.font = cv.InitFont(cv.CV_FONT_HERSHEY_PLAIN, 0.8, 0.8)
        self.font_time = cv.InitFont(cv.CV_FONT_HERSHEY_PLAIN, 1.8, 1.0, thickness=3)
        self.capture = cv.CaptureFromFile(VIDEO_FILE)
        self.frame_count = int(cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_COUNT))
        #self.frame_count = 200
        #print(self.frame_count)
        self.count = 0
        self.count_old = -1
        self.shift = int(N_SHIFT*0.5)
        self.wait = 400
        cv.NamedWindow("video_window")
        cv.CreateTrackbar("video_frame", "video_window", 0, self.frame_count,
                          self.on_change)
        cv.CreateTrackbar("gaze_shift", "video_window", self.shift, N_SHIFT,
                          self.on_shift)
        cv.CreateTrackbar("speed", "video_window", self.wait, 500,
                          self.on_speed)

        with open(DATA_PICKLE, "rb") as pfile:
            subjects, population = pickle.load(pfile)
        self.datas = subjects
        self.subject_names = ["vp" + str(ii) for ii in range(len(subjects))]
        self.gaze_indexs = [0 for i in range(len(self.datas))]
        self.points_list_before = [None for i in range(len(self.datas))]
        print(self.datas[0][0:10,])

        #codec = cv.CV_FOURCC('I', '4', '2', '0')
        codec = cv.CV_FOURCC('P', 'I', 'M', '1')
        width = int(cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_WIDTH))
        height = int(cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_HEIGHT))
        self.video_size = (width, height)
        outname = VIDEO_FILE + "out" + time.strftime("%Y%m%d_%H%M%S") + ".avi"
        self.writer = cv.CreateVideoWriter(outname, codec, OUT_FPS, self.video_size,
                                           1)
        print("VIDEO_FILE: %s" % VIDEO_FILE)
        print("frame_count: %i" % self.frame_count)
        print("width: %i" % width)
        print("height: %i" % height)
        print("data: %s" % DATA_PICKLE)
        time.sleep(2)

    def on_change(self, new_count):
        """
        Track bar callback in order to jump in the video (does not work
        properly).

        """
        #print "on_change: %i" % new_count
        self.count = new_count

    def on_shift(self, new_shift):
        """
        Track bar callback to change the shift between gaze data and video
        stream.

        """
        self.shift = new_shift

    def on_speed(self, new_wait):
        """
        Track bar callback to change the time that the program waits after each
        frame. Time is in milli seconds.

        """
        self.wait = new_wait

    def run(self):
        """
        Show the video and paint the gaze data on top.

        """
        x, y = 0, 0
        while self.count < self.frame_count:
            self.count = cv.GetTrackbarPos("video_frame", "video_window")
            image = cv.QueryFrame(self.capture)
            # was count changed by the user?
            if not self.count - 1 == self.count_old:
                print("change frame old/new: %i/%i" % (self.count_old, self.count) )
                #cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_POS_AVI_RATIO, ratio)
                cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_POS_FRAMES, self.count)

            points_list = self.get_gaze_data()
            time_ms = ((self.count - FRAME_GAME_START)*FRAME_LENGTH_MS +
                (self.shift - N_SHIFT*0.5)*10)
            secs = time_ms//1000 % 60
            minutes = time_ms//1000//60

            # draw clock
            text_time = "%i:%.2i" % (minutes, secs)
            cv.PutText(image, text_time, (self.video_size[0] - 79, 29), self.font_time, (0, 0, 0))
            cv.PutText(image, text_time, (self.video_size[0] - 80, 30), self.font_time, (255, 255, 255))

            # draw subjects
            for i_subject, points in enumerate(points_list):
                points_before = self.points_list_before[i_subject]
                if points is None or points_before is None:
                    continue
                try:
                    # only draw the first point as a fast heuristic
                    x0, y0, t0 = points_before[0]
                    x1, y1, t1 = points[0]
                    # black border on top
                    #y0 +=  -52.5
                    #y1 +=  -52.5
                    ## video: monitor -> screen
                    #x0 *= 1024/1680
                    #x1 *= 1024/1680
                    #y0 *= 576/945
                    #y1 *= 576/945
                    # 16:9 -> 5:4
                    #x *= 720/1024
                    # round to int
                    x0 = int(round(x0))
                    x1 = int(round(x1))
                    y0 = int(round(y0))
                    y1 = int(round(y1))
                    color = self.color_from_subject(i_subject)
                    #color = (255, 55, 55)
                    cv.Line(image, (x0, y0), (x1, y1), (0, 0, 0), 3)
                    cv.Line(image, (x0, y0), (x1, y1), color, 2)
                    cv.Circle(image, (x1, y1), 4, color, -1, 8, 0)
                    cv.Circle(image, (x1, y1), 4, (0, 0, 0), 1, 8, 0)
                    # upper left corner star graph
                    width, height = self.video_size
                    scale = 0.2
                    # width and height of the midpoint
                    width = int(width * scale)
                    height = int(height * scale)
                    cv.Rectangle(image, (0,0), (2*width, 2*height), (255, 255, 255))
                    cv.Line(image, (width, height), (int((x1 - x0) * scale) + width, int((y1 - y0) * scale) + height), (0, 0, 0), 3)
                    cv.Line(image, (width, height), (int((x1 - x0) * scale) + width, int((y1 - y0) * scale) + height), (255, 0, 0), 2)
                    #text = self.subject_names[i_subject]
                    #cv.PutText(image, text, (x1-8, y1+4), self.font, (0, 0, 0))
                except IndexError:
                    pass
            self.points_list_before = points_list

            if image is None:
                break
            cv.WriteFrame(self.writer, image)
            cv.ShowImage("video_window", image)
            if self.count in (862, 866, 876):
                #with open("data%i.pickle" % self.count, "w") as f:
                #    pickle.dump((points_list, self.points_list_before), f)
                arr = np.asarray(image[:,:])
                imsave('frame%i.png' % self.count, arr[:,:,::-1])
            if self.count + 1 >= self.frame_count:
                break
            self.count_old = self.count
            cv.SetTrackbarPos("video_frame", "video_window", self.count + 1)
            cv.WaitKey(self.wait + 2)

    def get_gaze_data(self):
        """
        Returns a list of np.arrays, that contain the points and the time (x,
        y, t).

        Calculates it from self.count and self.shift.

        """
        time = ((self.count - FRAME_GAME_START)*FRAME_LENGTH_MS*1000 +
                (self.shift - N_SHIFT*0.5)*10*1000)
        points_list = list()
        for i, gaze_data in enumerate(self.datas):
            try:
                last_point = True
                while gaze_data[self.gaze_indexs[i]][2] < time:
                    self.gaze_indexs[i] += 1
                    last_point = False
                if self.gaze_indexs[i] != 0 and not last_point:
                    points_list.append([gaze_data[self.gaze_indexs[i]],])
                elif last_point:
                    points_list.append(None)
            except IndexError:
                points_list.append(None)
        return points_list

    def color_from_subject(self, index):
        """
        Gives a color for a given subject index. e. g. one color for each
        group.

        """
        return (255 - 10 * index, 255 - 5 * index, 0)

if __name__ == "__main__":
    print("Initialize gaze track...")
    gaze_track = GazeTrack()
    print("Initialization done.\n")
    print("Start Video.")
    gaze_track.run()

