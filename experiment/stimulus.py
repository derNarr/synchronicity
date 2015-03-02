#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from __future__ import division

import math
import random

from psychopy import visual, core

from helper import create_run_trial, create_show_text


class BaseStim(object):
    """
    Base stimulus for moving dots.

    This class encapsulates the logic that all stimuli have in common.

    Abstract Class
    --------------
    Needs to implement:

    * self.objects : list
    * self.speed : int / float
    * self._move_objects(self) : function

    """

    def __init__(self, win, name, fps=60, start_pos=(0, 0)):
        """
        Parameters
        ----------
        win : psychopy.visual.Window
        name : str
        fps : int
        start_pos : (int, int)

        """
        self.win = win
        self.name = name
        self.fps = fps
        self.frame_counter = 0
        self.start_time = core.getTime()
        self.start_pos = start_pos
        #self.objects = list()
        #self.speed


    @property
    def flip_duration(self):
        """
        Flip duration in seconds.

        """
        return 1./self.fps


    @property
    def time(self):
        """
        Time the stimulus runs.

        """
        return core.getTime() - self.start_time


    def draw(self):
        """
        Draws the stimuli an increases the frame counter.

        """
        self._move_objects()
        for object_ in self.objects:
            object_.draw()
        self.frame_counter += 1


    def _move_objects(self):
        """
        Moves the objects, must be implemented by child class.

        """
        raise NotImplementedError()


    def __str__(self):
        return (str(self.__class__.__name__) + "_" + str(self.name)
                + ("_time%.2f" % self.start_time)
                + ("_speed%i" % int(self.speed)))


class HorizontalMovement(BaseStim):
    """
    Moves one circle from left to right.

    """

    def __init__(self, win, speed=100, *args, **kwargs):
        """
        Parameters
        ----------
        win : psychopy.visual.Window
        speed : speed of the stimulus in pixel per second

        """
        self.speed = speed
        self.objects = (visual.Circle(win, radius=20, fillColor=(1,1,1),
                                      units="pix"), )
        super(HorizontalMovement, self).__init__(win, *args, **kwargs)


    def _move_objects(self):
        #tt = self.frame_counter * self.flip_duration
        tt = self.time
        x_0, y_0 = self.start_pos
        circle = self.objects[0]
        circle.pos = (self.speed * tt + x_0, y_0)


class CircleMovement(BaseStim):
    """
    Moves one circle in a big circle. Round and Round.

    """

    def __init__(self, win, radius=200, speed=300, *args, **kwargs):
        """
        Parameters
        ----------
        win : psychopy.visual.Window
        radius : radius of the big circle
        speed : speed of the stimulus in pixel per second

        """
        self.radius = radius
        self.speed = speed
        self.objects = (visual.Circle(win, radius=20, fillColor=(1, 1, 1),
                                      units="pix"), )
        super(CircleMovement, self).__init__(win, *args, **kwargs)


    @property
    def angle_per_sec(self):
        return self.speed / self.radius


    def _move_objects(self):
        #tt = self.frame_counter * self.flip_duration
        tt = self.time
        x_0, y_0 = self.start_pos
        circle = self.objects[0]
        angle = self.angle_per_sec * tt
        xx = self.radius * math.cos(angle) + x_0 - self.radius
        yy = self.radius * math.sin(angle) + y_0
        # reflect
        circle.pos = (xx, yy)


class RandomBlink(BaseStim):
    """
    Circle blinks randomly over the display.

    """

    def __init__(self, win, random_positions, blink_every_frame=20, *args,
                 **kwargs):
        """
        Parameters
        ----------
        win : psychopy.visual.Window
        random_positions : sequence of pairs
        blink_every_frame : number of frames a blink should occur

        """
        self.random_positions = random_positions
        self.blink_every_frame = blink_every_frame

        self.objects = (visual.Circle(win, radius=20, fillColor=(1, 1, 1),
                                      units="pix"), )
        super(RandomBlink, self).__init__(win, *args, **kwargs)


    def _move_objects(self):
        # Note: didn't use start_pos
        circle = self.objects[0]
        idx = int(self.time // self.flip_duration // self.blink_every_frame)
        try:
            xx, yy = self.random_positions[idx]
        except IndexError:
            xx, yy = self.random_positions[-1]
        circle.pos = (xx, yy)


    @staticmethod
    def generate_random_positions(radius=150, size=24, start_pos=(0, 0),
                                  win_size=(1300, 700)):
        """
        Parameters
        ----------
        radius : blink radius in pixel
        size : number of random positions to generate
        start_pos : (int, int)
        win_size : (int, int)

        """
        pos = start_pos
        random_positions = [pos, ]
        for ii in range(size):
            xx, yy = pos
            angle = random.random() * 2 * math.pi
            dx = radius * math.cos(angle)
            dy = radius * math.sin(angle)
            # reflect
            if -win_size[0] / 2 <= xx + dx <= win_size[0] / 2:
                xx += dx
            else:
                xx -= dx
            if -win_size[1] / 2 <= yy + dy <= win_size[1] / 2:
                yy += dy
            else:
                yy -= dy
            pos = (xx, yy)
            random_positions.append(pos)
        return random_positions



class RandomWalk(BaseStim):
    """
    Circle moves over the display as it is described in an array.

    """

    def __init__(self, win, random_positions, *args, **kwargs):
        """
        Parameters
        ----------
        win : psychopy.visual.Window
        random_positions : list of pairs

        """
        self.random_positions = random_positions

        self.objects = (visual.Circle(win, radius=20, fillColor=(1,1,1),
                                      units="pix"), )
        super(RandomWalk, self).__init__(win, *args, **kwargs)


    def _move_objects(self):
        # Note: didn't use start_pos
        circle = self.objects[0]
        idx = int(self.time // self.flip_duration)
        try:
            xx, yy = self.random_positions[idx]
        except IndexError:
            xx, yy = self.random_positions[-1]
        circle.pos = (xx, yy)


    @staticmethod
    def generate_random_positions(speed=800, dangle=90/180*math.pi, size=480,
                                  start_pos=(0, 0), win_size=(1300, 700),
                                  flip_duration=1/60):
        """
        Parameters
        ----------
        speed : int
            speed in pixel per second
        dangle : float
            range of an angle in rad that changes the current angle every flip
        size : int
            number of random positions to generate
        start_pos : (int, int)
        win_size : (int, int)
        flip_duration : float
            in seconds

        """
        pos = start_pos
        random_positions = [pos, ]
        angle = random.random() * 2 * math.pi
        for ii in range(size):
            xx, yy = pos

            dv = speed * flip_duration
            angle += random.random() * dangle - dangle / 2
            dx = dv * math.cos(angle)
            dy = dv * math.sin(angle)
            # reflect
            if -win_size[0] / 2 <= xx + dx <= win_size[0] / 2:
                xx += dx
            else:
                angle += math.pi / 2
                xx -= dx
            if -win_size[1] / 2 <= yy + dy <= win_size[1] / 2:
                yy += dy
            else:
                angle += math.pi / 2
                yy -= dy
            pos = (xx, yy)
            random_positions.append(pos)

        return random_positions


class MoveStopMove(BaseStim):
    """
    Moves one circle from left to right and stops it at a given time.

    """

    def __init__(self, win, speed=100, stop_t=1.0, stop_dur=1.0, *args,
                 **kwargs):
        """

        .. warning::

            This stimulus only works for left to right movement, i. e. positive
            speeds.

        Parameters
        ----------
        win : psychopy.visual.Window
        speed : int
            speed of the stimulus in pixel per second
        stop_t : float
            time to stop
        stop_dur : float
            duration how long circle stops

        """
        self.stop_t = stop_t
        self.stop_dur = stop_dur
        self.speed = speed
        self.objects = (visual.Circle(win, radius=20, fillColor=(1,1,1),
                                      units="pix"), )
        super(MoveStopMove, self).__init__(win, *args, **kwargs)


    def _move_objects(self):
        #tt = self.frame_counter * self.flip_duration
        x_0, y_0 = self.start_pos
        tt = self.time

        # wait and correct time
        if self.stop_t < tt <= self.stop_t + self.stop_dur:
            tt = self.stop_t
        elif tt > self.stop_t + self.stop_dur:
            tt -= self.stop_dur

        circle = self.objects[0]
        circle.pos = (self.speed * tt + x_0, y_0)


class MoveExplodeMove(BaseStim):
    """
    Moves one circle from left to right and explodes it at a given time.

    """

    def __init__(self, win, speed=300, explode_t=0, explode_dur=1.0,
                 radius=150, *args, **kwargs):
        """

        .. warning::

            This stimulus only works for left to right movement, i. e. positive
            speeds.

        Parameters
        ----------
        win : psychopy.visual.Window
        speed : int
            speed of the stimulus in pixel per second
        explode_t : float
            time at that the explosion is triggered
        explode_dur : float
            duration how long circle explodes
        radius : float
            radius of the explosion in pixel

        """
        self.explode_t = explode_t
        self.explode_dur = explode_dur
        self.speed = speed
        self.radius = radius
        self.circles = (visual.Circle(win, radius=20, fillColor=(1,1,1),
                                    units="pix"), )
        self.explosion = (
            visual.Circle(win, radius=10, fillColor=(1,1,1), units="pix"),
            visual.Circle(win, radius=10, fillColor=(1,1,1), units="pix"),
            visual.Circle(win, radius=10, fillColor=(1,1,1), units="pix"),
            visual.Circle(win, radius=10, fillColor=(1,1,1), units="pix"),
            visual.Circle(win, radius=10, fillColor=(1,1,1), units="pix"),
            visual.Circle(win, radius=10, fillColor=(1,1,1), units="pix"),
        )
        super(MoveExplodeMove, self).__init__(win, *args, **kwargs)


    def _trajectory(self, tt):
        x_0, y_0 = self.start_pos
        return (self.speed * tt + x_0, y_0)


    def _move_objects(self):
        #tt = self.frame_counter * self.flip_duration
        tt = self.time

        # wait and correct time
        if self.explode_t < tt <= self.explode_t + self.explode_dur:
            tt = self.explode_t
            self.objects = self.explosion
            nn = len(self.explosion)
            for ii, circle in enumerate(self.objects):
                xx, yy = self._trajectory(tt)
                xx += self.radius * math.cos(2 * math.pi * ii / nn)
                yy += self.radius * math.sin(2 * math.pi * ii / nn)
                circle.pos = (xx, yy)
            return
        elif tt > self.explode_t + self.explode_dur:
            tt -= self.explode_dur

        self.objects = self.circles
        circle = self.objects[0]
        circle.pos = self._trajectory(tt)


if __name__ == "__main__":
    win = visual.Window(size=(1280, 720))
    text_stim = visual.TextStim(win)
    fixation_cross = visual.TextStim(win, '+', height=25, units='pix')

    eye_tracker = type("EyeTracker", (object,), {})()  # creates an instance of an empty class
    eye_tracker.sendImageMessage = lambda x: None
    def calibrate():
        print("calibration done")

    show = create_show_text(win, text_stim, calibrate)
    run_trial = create_run_trial(win, eye_tracker, calibrate, fixation_cross)

    hori = HorizontalMovement(win, name="hori300", speed=800, start_pos=(-380, 0))
    cm = CircleMovement(win, name="cm", radius=200)
    msm = MoveStopMove(win, name="msm300", speed=300, stop_dur=1.0,
                       start_pos=(-600, 0))
    mem = MoveExplodeMove(win, name="mem300", speed=300, start_pos=(-600, 0))
    rw = RandomWalk(win,
                    RandomWalk.generate_random_positions(win_size=(1280, 720),
                                                         speed=400),
                    name="rw300")
    rb = RandomBlink(win,
                     RandomBlink.generate_random_positions(win_size=(800, 600),
                                                           radius=200),
                     name="rb200",
                     blink_every_frame=60)

    show(u"Schön, dass Sie an diesem Experiment teilnehmen.\n\nWeiter mit der Leertaste.",
         wait_keys=('space',))

    show("RadomBlink")
    run_trial(rb, duration=2.0)

    show("RadomWalk")
    run_trial(rw, duration=8.0)

    show("CircleMovement")
    run_trial(cm, duration=3.0, speed=600)

    show("HorizontalMovement")
    run_trial(hori, duration=1.0, speed=800)

    show("MoveStopMove")
    run_trial(msm, duration=3.0)

    show("MoveExplodeMove")
    run_trial(mem, duration=3.0)

    show(u"Vielen Dank für Ihre Teilnahme an diesem Experiment.\n\nBitte melden Sie sich beim Versuchsleiter.",
         wait_keys=('escape',))

