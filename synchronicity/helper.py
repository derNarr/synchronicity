#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# helper.py

"""
Helper and utility functions.

"""

from __future__ import division

import numpy as np


def parse_smi(files):
    """
    Return parsed files as list of dicts.

    .. note:
        parse_smi uses the x and y coordinate of the left eye.

    Parameters
    ----------
    files : sequence of str
        file names. For every subject one tab separated file.

    Returns
    -------
    subjects : sequence of dicts
        every dict has a value for "data", "msg" and "file_name".
        * A value in "data" contains of the x, y and time coordinate.
        * A value in "msg" contains of the time coordinate and a string.
        * "file_name" contains the file name

    Raises
    ------
    IOError : wrong format
        If the format of the tab separated file does not fit the assumptions
        parse_smi raises an IOError.

    """
    subjects = list()
    for f in files:
        with open(f, "r") as data_file:
            header_found = False
            data = list()
            msg = list()
            for line in  data_file:
                # skip all commentary
                if line[0] == "#":
                    continue
                parts = line.split("\t")
                if parts[0] == "Time":
                    header_found = True
                    print(line)
                    # check header
                    if (parts[3] != "L POR X [px]" or
                        parts[4] != "L POR Y [px]"):
                        raise IOError("Header of %s has wrong format." % f)
                    continue
                if parts[1] == "MSG":
                    print(line)
                    msg_point = (float(parts[0]), parts[3])
                    msg.append(msg_point)
                    continue
                if parts[1] == "SMP":
                    if not header_found:
                        raise IOError("No header was found before the first line of data.")
                    data_point = (float(parts[3]), # X left eye
                                float(parts[4]), # Y left eye
                                float(parts[0])) # time
                    data.append(data_point)
                    continue
            subjects.append({"data": data, "msg": msg, "file_name": f})
    return subjects


def parse_coord(files):
    """
    Return parsed files as list of np.arrays.

    Parameters
    ----------
    files : sequence of str
        file names. For every subject one tab separated file.

    Returns
    -------
    Sequence of np.arrays. One array per subject. With (x, y, t)

    """
    subjects = list()
    for f in files:
        raw = np.loadtxt(f, skiprows=2)
        clean = raw[raw[:, 3] != 0]
        unordered = clean[:, :3] # remove last column
        data = unordered[:, (1, 2, 0)] # (t, x, y) -> (x, y, t)
        subjects.append(data)
    return subjects


def extract_video_data(subjects, video):
    """
    extract eye samples for video by collecting all samples between the
    message, that the video starts up to the next message.

    .. note::
        The exported smi text file must include the messages.

    Parameters
    ----------
    subjects : sequence
        sequence of dicts including the data and the messages for each subject
        (the format smi_parse returns)
    video : string
        name of the video used in the message output

    Returns
    -------
    Sequence of np.arrays. The first n_1 arrays for the first subject (when
    n_1, n_2,... are the number of repetitions of each subject) the second n_2
    arrays correspond to the second subject etc.

    """
    gaze_data = list()
    for subject in subjects:
        data = np.array(subject["data"])
        msgs = np.array(subject["msg"])
        starts = list()
        stops = list()
        for i, msg in enumerate(msgs):
            if msg[1].split(" ")[2].strip() == video:
                starts.append(float(msg[0]))
                try:
                    stops.append(float(msgs[i+1][0]))
                except IndexError:
                    pass
        for i, start in enumerate(starts):
            try:
                stop = stops[i]
                # slice intervall
                tmp = data[data[:,2] > start,:]
                tmp = tmp[tmp[:,2] < stop,:]
                # adjust time
                tmp[:,2] -= start
                gaze_data.append(tmp)
            except IndexError:
                # slice intervall
                tmp = data[data[:,2] > start,:]
                # adjust time
                tmp[:,2] -= start
                gaze_data.append(tmp)
    return gaze_data


def slice_time_window(gaze_data, t=112.5, dt=225):
    """
    Returns a sliced np.array.

    The slice in gaze_data have the center time of t and
    an interval of length dt i. e. dt/2 in both directions.

    Parameters
    ----------
    gaze_data : np.array
        data to be sliced with columns x, y, t
    t : float
        center time of the slice
    dt : float
        width of the slice. The slice will extend dt/2 in both directions of t.

    Returns
    -------
    slice : np.array
        slice of gaza_data

    """
    slice_ = gaze_data[gaze_data[:,2] >= t - dt/2]
    if len(slice_) == 0:
        print("WARNING: empty slice")
        return slice_
    slice_ = slice_[slice_[:,2] <= t + dt/2]
    if len(slice_) == 0:
        print("WARNING: empty slice")
    return slice_


def random_uniform_sample(n, screen_res, t, dt):
    norm_sample_x = np.random.uniform(0, screen_res[0], n)
    norm_sample_y = np.random.uniform(0, screen_res[1], n)
    norm_sample_t = np.random.uniform(t - dt/2, t + dt/2, n)
    return np.array((norm_sample_x, norm_sample_y, norm_sample_t)).transpose()


def velocity(gaze_data, dt_max, euclidean=False):
    """
    Calculates the velocity of the gazes in gaze_data.

    Parameters
    ----------
    gaze_data : np.array
        gaze data that are used to generate the velocities
    dt_max : float
        if the time difference between to measurements in gaza_data is larger
        than dt_max the corresponding velocity is dropped

    Returns
    -------
    velocities : np.array
        v_r, v_phi, t where v_r and v_phi are the components of the velocity in
        polar coordinates and t is mean of the times of the underling locations
        (v_x, v_y, v_t if euclidean=True)

    """
    sorted_gaze_data = gaze_data[np.argsort(gaze_data[:, 2])]  # sort along time
    dt = sorted_gaze_data[1:, 2] - sorted_gaze_data[:-1, 2]  # might produce zeros
    dx = sorted_gaze_data[1:, 0] - sorted_gaze_data[:-1, 0]
    dy = sorted_gaze_data[1:, 1] - sorted_gaze_data[:-1, 1]

    # keep only velocities where dt is strictly greater than zero and less or
    # equal to dt_max
    mask = (0 < dt) & (dt <= dt_max)

    dt = dt[mask]
    v_x = dx[mask] / dt
    v_y = dy[mask] / dt
    v_t = sorted_gaze_data[:-1, 2][mask] + dt / 2
    del mask

    if euclidean:
        return np.array((v_x, v_y, v_t)).transpose()

    # else use polar coordinates
    v_r = np.sqrt(v_x ** 2 + v_y ** 2)
    v_phi = np.empty_like(v_r)

    mask = v_r != 0
    notmask = v_r == 0
    v_phi[mask] = np.arctan2(v_y[mask], v_x[mask])
    v_phi[notmask] = np.NaN

    return np.array((v_r, v_phi, v_t)).transpose()

