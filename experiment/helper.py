#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from __future__ import division

from psychopy import core, event


class CalibrationNeed(Exception):
    """
    Raised when the eye tracker needs a recalibration.

    """
    pass


def create_run_trial(win, eye_tracker, calibrate, fixation_cross):
    """
    Creates the run_trial function.

    Parameters
    ----------
    win : psychopy.visiual.Window
    eye_tracker : EyeTracker
    calibrate : function
    fixation_cross : psychopy.visual.TextStim

    """

    def run_trial(stimulus, duration=1.0, speed=400):
        """
        Runs one trial with stimulus.

        Parameters
        ----------
        duration : float
            duration of the trial in seconds
        speed : int
            speed of the stimulus in pixels per second

        """
        run = True
        while run:
            try:
                for i in range(30):
                    fixation_cross.setPos(stimulus.start_pos)
                    fixation_cross.draw()
                    win.flip()
                start_time = core.getTime()
                stimulus.start_time = start_time
                stimulus.speed = speed
                # monkey patch explode_t and stop_t
                # bad style!
                stimulus.explode_t = (duration - 1.0) / 2
                stimulus.stop_t = (duration - 1.0) / 2
                # bad style end
                eye_tracker.sendImageMessage(str(stimulus))
                while core.getTime() < start_time + duration:
                    stimulus.draw()
                    win.flip()
                    for key in event.getKeys():
                        if key in ("c", "C", "k", "K"):
                            raise CalibrationNeed('manual')
                run = False
                eye_tracker.sendImageMessage("Done_" + str(stimulus))
            except CalibrationNeed:
                calibrate()

    return run_trial


def create_run_movie(win, eye_tracker, calibrate, show_text):
    """
    Creates the run_movie function.

    Parameters
    ----------
    win : psychopy.visiual.Window
    eye_tracker : EyeTracker
    calibrate : function
    show_text : function

    """

    def run_movie(movie, instruction="Continue with space."):
        """
        Runs movie.

        Parameters
        ----------
        movie : psychopy.visiual.MovieStim
        instruction : str

        """
        run = True
        while run:
            try:
                show_text(instruction, wait_keys=('space', ))
                #movie.seek(0)
                start_time = core.getTime()
                duration = movie.duration
                eye_tracker.sendImageMessage(str(movie))
                while core.getTime() < start_time + duration:
                    movie.draw()
                    win.flip()
                    for key in event.getKeys():
                        if key in ("c", "C", "k", "K"):
                            eye_tracker.sendImageMessage("Recalibration.")
                            raise CalibrationNeed('manual')
                run = False
                eye_tracker.sendImageMessage("Done_" + str(movie))
            except CalibrationNeed:
                calibrate()

    return run_movie


def create_show_text(win, text_stim, calibrate):
    """
    Creates the show_text function.

    """

    def show_text(text, wait_keys=None, duration=1.0):
        """
        Shows the text on the screen. Waits for any key in wait_keys. If
        wait_keys is None continue after duration.

        """
        text_stim.setText(text)
        if wait_keys is None:
            start_time = core.getTime()
            while core.getTime() <= start_time + duration:
                text_stim.draw()
                win.flip()
                for key in event.getKeys():
                    if key in ("c", "C", "k", "K"):
                        calibrate()
        else:
            run = True
            while run:
                text_stim.draw()
                win.flip()
                for key in event.getKeys():
                    if key in ("c", "C", "k", "K"):
                        calibrate()
                    if key in wait_keys:
                        run = False

    return show_text


def create_calibrate(win, text_stim, eye_tracker):
    """
    Creates calibrate function.

    """

    def calibrate():
        """
        (Re-)calibrates the eye tracker and waits within psychopy in order to
        continue the experiment.

        """
        event.clearEvents()
        core.wait(0.2)
        eye_tracker.calibrateAndValidateWithExperimenterFeedback(intentedMaxDeviation=0.8)
        event.clearEvents()
        text_stim.setText("Kalibrierung erfolgreich.\n\nWeiter mit Leertaste")
        while not "space" in event.getKeys():
            text_stim.draw()
            win.flip()

    return calibrate

