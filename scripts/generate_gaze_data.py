#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# generate_gaze_data.py

"""
Generate specific idealized gaze patterns for several subjects to use them
as benchmark for the different coherence algorithms.

All functions return a sequence of n elements. Each element is a nx3
np.array containing the (x, y, t) data points for one subject.

Time is given in micro seconds (us).

"""

import pickle

import numpy as np

SCREEN_RES = (1280, 720)
SAMPLING_RATE = 50 #Hz
DELTA_T = 1./float(SAMPLING_RATE) * 1000000
SD_NOISE = 5

def random_coherent_random(n, dt, t1, t2):
    """
    generate random coherent random data.

    Parameters
    ----------
    n : integer
        number of subjects
    dt : float
        time intervall in micro seconds
    t1 : float
        point in time where coherent phase begins
    t2 : float
        point in time where coherent phase ends

    Returns
    -------
    subjects : sequence of np.arrays

    """
    subjects = list()
    time_steps = int(dt/DELTA_T)
    x_coherent = np.random.normal(SCREEN_RES[0]/2., SCREEN_RES[0]/6.)
    y_coherent = np.random.normal(SCREEN_RES[1]/2., SCREEN_RES[1]/6.)
    for i in range(n):
        subject = list()
        state = None
        for j in range(time_steps):
            t = j * DELTA_T
            x_noise = np.random.normal(0, SD_NOISE)
            y_noise = np.random.normal(0, SD_NOISE)
            # random
            if t < t1:
                if not state == "random1":
                    state = "random1"
                    x_state = np.random.normal(SCREEN_RES[0]/2., SCREEN_RES[0]/6.)
                    y_state = np.random.normal(SCREEN_RES[1]/2., SCREEN_RES[1]/6.)
                x = x_state + x_noise
                y = y_state + y_noise
            elif t < t2:
                if not state == "coherent":
                    state = "coherent"
                x = x_coherent + x_noise
                y = y_coherent + y_noise
            else:
                if not state == "random2":
                    state = "random2"
                    x_state = np.random.normal(SCREEN_RES[0]/2., SCREEN_RES[0]/6.)
                    y_state = np.random.normal(SCREEN_RES[1]/2., SCREEN_RES[1]/6.)
                x = x_state + x_noise
                y = y_state + y_noise
            subject.append((x, y, t))
        subject = np.array(subject)
        subjects.append(subject)
    return subjects

def random_intervals(n, dt, ts):
    """
    generate random coherent random data.

    Parameters
    ----------
    n : integer
        number of subjects
    dt : float
        time intervall in micro seconds
    ts : list of float
        points in time where random phase switches

    Returns
    -------
    subjects : sequence of np.arrays

    """
    subjects = list()
    time_steps = int(dt/DELTA_T)
    for i in range(n):
        subject = list()
        state = None
        for j in range(time_steps):
            t = j * DELTA_T
            x_noise = np.random.normal(0, SD_NOISE)
            y_noise = np.random.normal(0, SD_NOISE)
            for t_int in ts:
                if t < t_int:
                    if not state == t_int:
                        state = t_int
                        x_state = np.random.normal(SCREEN_RES[0]/2., SCREEN_RES[0]/6.)
                        y_state = np.random.normal(SCREEN_RES[1]/2., SCREEN_RES[1]/6.)
                    x = x_state + x_noise
                    y = y_state + y_noise
                    break
            if t > ts[-1]:
                if not state == "last":
                    state = "last"
                    x_state = np.random.normal(SCREEN_RES[0]/2., SCREEN_RES[0]/6.)
                    y_state = np.random.normal(SCREEN_RES[1]/2., SCREEN_RES[1]/6.)
                x = x_state + x_noise
                y = y_state + y_noise
            subject.append((x, y, t))
        subject = np.array(subject)
        subjects.append(subject)
    return subjects

def find_the_needle(n, dt_interval, n_before, n_after):
    """
    generate random coherent random data.

    The total time interval is equal to dt_interval*(n_before+n_after+1).

    Parameters
    ----------
    n : integer
        number of subjects
    dt_interval : float
        length of single interval in micro seconds
    n_before : integer
        number of intervals before the coherent interval
    n_after : integer
        number of intervals after the coherent interval

    Returns
    -------
    subjects : sequence of np.arrays

    """
    subjects = list()
    dt = dt_interval * (n_before + 1 + n_after)
    print("dt: %f" % dt)
    time_steps = int(dt/DELTA_T)
    x_coherent = np.random.normal(SCREEN_RES[0]/2., SCREEN_RES[0]/6.)
    y_coherent = np.random.normal(SCREEN_RES[1]/2., SCREEN_RES[1]/6.)
    for i in range(n):
        subject = list()
        state = None
        for j in range(time_steps):
            t = j * DELTA_T
            x_noise = np.random.normal(0, SD_NOISE)
            y_noise = np.random.normal(0, SD_NOISE)
            for k in range(n_before):
                t_int = (k+1) * dt_interval
                if t < t_int:
                    if not state == t_int:
                        state = t_int
                        x_state = np.random.normal(SCREEN_RES[0]/2., SCREEN_RES[0]/6.)
                        y_state = np.random.normal(SCREEN_RES[1]/2., SCREEN_RES[1]/6.)
                    x = x_state + x_noise
                    y = y_state + y_noise
                    break
            if n_before*dt_interval < t < (n_before+1)*dt_interval:
                if not state == "coherent":
                    state = "coherent"
                x = x_coherent + x_noise
                y = y_coherent + y_noise
            if t > (n_before+1)*dt_interval:
                for k in range(n_after):
                    t_int = (n_before + 1 + k+1) * dt_interval
                    if t < t_int:
                        if not state == t_int:
                            state = t_int
                            x_state = np.random.normal(SCREEN_RES[0]/2., SCREEN_RES[0]/6.)
                            y_state = np.random.normal(SCREEN_RES[1]/2., SCREEN_RES[1]/6.)
                        x = x_state + x_noise
                        y = y_state + y_noise
                        break
            if t > (n_before+1+n_after)*dt_interval:
                if not state == "last":
                    state = "last"
                    x_state = np.random.normal(SCREEN_RES[0]/2., SCREEN_RES[0]/6.)
                    y_state = np.random.normal(SCREEN_RES[1]/2., SCREEN_RES[1]/6.)
                x = x_state + x_noise
                y = y_state + y_noise
            subject.append((x, y, t))
        subject = np.array(subject)
        subjects.append(subject)
    return subjects



if __name__ == "__main__":
    subjects = find_the_needle(20, 300000, 50, 50)
    population = np.concatenate(subjects, axis=0)
    pickle_file = "find_the_needle.pickle"
    with open(pickle_file, "wb") as pfile:
        obj = (subjects, population)
        pickle.dump(obj, pfile)

