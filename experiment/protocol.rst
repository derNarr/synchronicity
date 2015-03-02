========
Protocol
========

Experiment
==========
In order to run the experiment run::

    python exp.py


Preparations
============
In order to generate session files and random items run::

    python generate_sessionfiles.py

Setup
=====

* distance head rest vs monitor 64 cm
* eye position 8 cm below upper border of monitor
* eye position horizontally centered
* monitor width 38 cm, height 30.5 cm

Conditions
==========
Window resolution 1280x1024

Start Positions
---------------
Measured in pixels::

    xx = -560
    yys = (-90, 0, 90)

Speed
-----
Measured in pixel per second::

    speeds = (150, 200, 300, 400, 600, 800)

This corresponds to presentations times in seconds for 60 Hz for the
HorizontalMovment of::

    times = (8, 6, 4, 3, 2, 1.5)


Radius for CircleMovement
-------------------------
Measured in pixels::

    radiis = (100, 200, 400)


Number of Trials
----------------
HorizontalMovement::

    18 = 3 (pos) * 6 (speed)

MoveStopMove::

    18 = 3 (pos) * 6 (speed)

CircleMovement::

    18 = 6 (speed) * 3 (radiis)

MoveExplodeMove::

    18 = 6 (speed) * 3 (radiis)

RadomWalk::

    25

RandomBlink::

    25


Total::

    122 = 4 * 18 + 2 * 25

Time needed::

    time_needed = ((2 * 25 + 18) * 8.5  # Random + Circle
        + 3 * (8.5 + 6.5 + 4.5 + 3.5 + 2.5 + 2.0)  # Horizontal
        + 6 * (9.5 + 7.5 + 5.5 + 4.5 + 3.5 + 3.0)  # Stop + Explode
        + 6 * 30  # breaks
        + 240  # big buck bunny part 1
        + 280)  # big buck bunny part 2

