#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from __future__ import division

import random
import os
import math
import pickle

import stimulus

WIN_SIZE = (1280, 1024)
FPS = 60
N_RANDOM_TRIALS = 25

def create_random_items():
    """
    Creates pickle files with lists of random positions for RandomWalk and
    RandomBlink stimuli.

    """
    for stimulus_nr in range(N_RANDOM_TRIALS):
        with open(os.path.join("random_items", "stim_walk_%02i.pickle" % stimulus_nr),
                  "w") as stim_file:
            random_positions = stimulus.RandomWalk.generate_random_positions(
                    speed=400,
                    dangle=90/180*math.pi,
                    size=60*9,
                    start_pos=(0, 0),
                    win_size=WIN_SIZE,
                    flip_duration=1/FPS)
            pickle.dump(random_positions, stim_file)
        with open(os.path.join("random_items", "stim_blink_%02i.pickle" %
                               stimulus_nr), "w") as stim_file:
            random_positions = stimulus.RandomBlink.generate_random_positions(
                    radius=200,
                    size=24,
                    start_pos=(0, 0),
                    win_size=WIN_SIZE)
            pickle.dump(random_positions, stim_file)


if __name__ == "__main__":

    random.seed(20141020)

    create_random_items()

    positions = (0, 1, 2)  # yy = -90, 0, +90
    speeds = (150, 200, 300, 400, 600, 800)
    durations = (8, 6, 4, 3, 2, 1.5)
    radiis = (100, 200, 400)
    break_ = "show(u'Machen Sie eine kurze Pause.\\n\\nWeiter mit Leertaste.', wait_keys=('space',))\n"

    trials = list()

    for base in ("hori", "mem", "msm"):
        for pos in positions:
            for ii, speed in enumerate(speeds):
                dur = durations[ii]
                if base in ("mem", "msm"):
                    dur += 1.0
                trials.append("run_trial(%s%i, duration=%.3f, speed=%i)" %
                              (base, pos, dur, speed))

    for radius in radiis:
        for speed in speeds:
            trials.append("run_trial(cm%i, duration=8.0, speed=%i)" % (radius,
                                                                       speed))

    for nr in range(N_RANDOM_TRIALS):
        trials.append("run_trial(rbs[%i], duration=8.0)" % nr)
        trials.append("run_trial(rws[%i], duration=8.0)" % nr)

    print(len(trials))

    for vpnr in range(1, 57):
        random.shuffle(trials)
        with open(os.path.join("sessions", "ses_vp%02i.py" % vpnr),
                  "w") as ses_file:
            ses_file.write("# vpnr %i\n" % vpnr)
            for ii in range(len(trials)):
                ses_file.write(trials[ii])
                ses_file.write("\n")
                if ii % 21 == 20:
                    ses_file.write(break_)
                    ses_file.write("\n")

            ses_file.write("\n")
            if vpnr % 2 == 0:
                ses_file.write("run_movie(movie1audio, 'Jetzt folgt ein Video mit Ton.\\n\\nWeiter mit Leertaste')\n"
                               + "run_movie(movie2noaudio, 'Jetzt folgt ein Video OHNE Ton.\\n\\nWeiter mit Leertaste')\n")
            elif vpnr % 2 == 1:
                ses_file.write("run_movie(movie1noaudio, 'Jetzt folgt ein Video OHNE Ton.\\n\\nWeiter mit Leertaste')\n"
                               + "run_movie(movie2audio, 'Jetzt folgt ein Video mit Ton.\\n\\nWeiter mit Leertaste')\n")


