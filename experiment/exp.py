#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from __future__ import division

import os
import time
import pickle
import shutil

from psychopy import visual, core, gui, misc, event

from EyeTracking import EyeTracker
import stimulus
from helper import (create_show_text, create_run_trial, create_calibrate,
                    create_run_movie)


SESSIONS_DIR = "./sessions/"

INSTRUCTION = u"""Sie werden in der Folge mehrere kurze Sequenzen eines weißen Punktes sehen, der über den grauen Monitor wandert. Bitte folgen Sie diesem weißen Punkt mit den Augen. Manchmal zerspringt der weiße Punkt in mehrere kleine weiße Punkte, dann schauen Sie einfach auf einen von diesen.\nAlle zwei bis drei Minuten gibt es eine kurze Pause.\n\nWeiter mit der Leertaste."""


def experiment():
    """
    Runs the whole experiment.

    """
    # create objects
    #win = visual.Window(size=(1366, 768), allowGUI=False)
    win = visual.Window(size=(1280, 1024), fullscr=False, screen=0,
                        allowGUI=False, allowStencil=False,
                        monitor='SMI-19Zoll', color=(0, 0, 0),
                        colorSpace='rgb', blendMode='avg', useFBO=True,
                        units='pix')
    text_stim = visual.TextStim(win)
    fixation_cross = visual.TextStim(win, '+', height=25, units='pix')
    #eye_tracker = EyeTracker.DummyEyeTracker()
    eye_tracker = EyeTracker.SmiEyeTracker("192.168.10.100", 4444,
                                           "192.168.10.101", 5555)

    # create helper functions
    calibrate = create_calibrate(win, text_stim, eye_tracker)
    show = create_show_text(win, text_stim, calibrate)
    run_trial = create_run_trial(win, eye_tracker, calibrate, fixation_cross)
    run_movie = create_run_movie(win, eye_tracker, calibrate, show)

    # create stimuli

    # speed is defined by run_trial calls in session file
    # stop_t, explode_t as well (with bad style monkey patching)
    hori0 = stimulus.HorizontalMovement(win, name="hori0", start_pos=(-560, -90))
    hori1 = stimulus.HorizontalMovement(win, name="hori1", start_pos=(-560, 0))
    hori2 = stimulus.HorizontalMovement(win, name="hori2", start_pos=(-560, 90))
    cm100 = stimulus.CircleMovement(win, name="cm100", radius=100, start_pos=(100, 0))
    cm200 = stimulus.CircleMovement(win, name="cm200", radius=200, start_pos=(200, 0))
    cm400 = stimulus.CircleMovement(win, name="cm400", radius=400, start_pos=(400, 0))
    msm0 = stimulus.MoveStopMove(win, name="msm0", stop_dur=1.0, start_pos=(-560, -90))
    msm1 = stimulus.MoveStopMove(win, name="msm1", stop_dur=1.0, start_pos=(-560, 0))
    msm2 = stimulus.MoveStopMove(win, name="msm2", stop_dur=1.0, start_pos=(-560, 90))
    mem0 = stimulus.MoveExplodeMove(win, name="mem0", explode_dur=1.0, start_pos=(-560, -90))
    mem1 = stimulus.MoveExplodeMove(win, name="mem1", explode_dur=1.0, start_pos=(-560, 0))
    mem2 = stimulus.MoveExplodeMove(win, name="mem2", explode_dur=1.0, start_pos=(-560, 90))

    rws = list()
    files = [f for f in os.listdir("random_items") if f[5:9] == "walk"]
    for ii, file_ in enumerate(files):
        with open(os.path.join("random_items", file_), "rb") as pfile:
            random_pos = pickle.load(pfile)
        rws.append(stimulus.RandomWalk(win, name="rws[%i]_%s" % (ii, file_),
                                       random_positions=random_pos))
    rbs = list()
    files = [f for f in os.listdir("random_items") if f[5:10] == "blink"]
    for ii, file_ in enumerate(files):
        with open(os.path.join("random_items", file_), "rb") as pfile:
            random_pos = pickle.load(pfile)
        rbs.append(stimulus.RandomBlink(win, name="rbs[%i]_%s" % (ii, file_),
                                        random_positions=random_pos,
                                        blink_every_frame=60))

    movie1audio = visual.MovieStim(win, "videos/first_audio.avi", flipHoriz=True)
    movie1noaudio = visual.MovieStim(win, "videos/first_noaudio.avi", flipHoriz=True)
    movie2audio = visual.MovieStim(win, "videos/second_audio.avi", flipHoriz=True)
    movie2noaudio = visual.MovieStim(win, "videos/second_noaudio.avi", flipHoriz=True)


    ## test movies

    #start_time = core.getTime()
    ## text correct?
    #while core.getTime() < 25 + start_time:
    #    movie1audio.draw()
    #    win.flip()

    #start_time = core.getTime()
    ## text correct?
    #while core.getTime() < 25 + start_time:
    #    movie1noaudio.draw()
    #    win.flip()

    #start_time = core.getTime()
    ## moves to right?
    #while core.getTime() < 10 + start_time:
    #    movie2audio.draw()
    #    win.flip()

    #start_time = core.getTime()
    ## moves to right?
    #while core.getTime() < 10 + start_time:
    #    movie2noaudio.draw()
    #    win.flip()


    # read in vpn info
    # try to load last exp infos
    try:
        exp_info = misc.fromFile('last_exp_info.pickle')
    except:
        exp_info = {'Versuchsleiter':'kose', 'Versuchsperson':'vp99',
                    'Sessionfile':'ses_vp99.py'}

    exp_info['Datum'] = time.strftime("%Y%m%d_%H%M", time.localtime())

    # present a dialogue to change infos
    event.Mouse().setVisible(True)
    dlg = gui.DlgFromDict(exp_info, title=u'Blicksynchronizität',
                          fixed=['Datum'])
    if dlg.OK:
        misc.toFile('last_exp_info.pickle', exp_info)
        # save params to file for next time
    else:
        core.quit()
        # the user hit cancel so exit
    event.Mouse().setVisible(False)

    if exp_info['Sessionfile'][4:8] != exp_info['Versuchsperson']:
        print("inconsistent sessionfile name")
        core.quit()

    # run experiment
    show(u"Schön, dass Sie an diesem Experiment teilnehmen."
             + "\n\nWeiter mit der Leertaste.", wait_keys=('space',))
    calibrate()
    try:
        eye_tracker.startRecording(exp_info['Versuchsperson'],
                                   savePath="D:/FrankPapenmeier-2014-10-20/KSS14/data/EyeTracking/")
        show(INSTRUCTION, wait_keys=('space',))
        show(u"Wenn Sie den Kopf aus der Kinnstütze nehmen müssen oder wollen, dann gebe Sie kurz bescheid, damit wir Sie dann neu kalibrieren können.\n\nWeiter mit der Leertaste.", wait_keys=("space",))
        show(u"Noch Fragen?\nJetzt geht es gleich los.\n\nWeiter mit der Leertaste.", wait_keys=('space',))
        execfile(os.path.join(SESSIONS_DIR, exp_info['Sessionfile']))
    finally:
        eye_tracker.stopAndSaveRecording()

    show(u"Vielen Dank für Ihre Teilnahme an diesem Experiment.\n\nBitte melden Sie sich beim Versuchsleiter.",
         wait_keys=('escape',))
    shutil.move(os.path.join(SESSIONS_DIR, exp_info["Sessionfile"]), os.path.join(SESSIONS_DIR, "done/"))


if __name__ == "__main__":
    experiment()

