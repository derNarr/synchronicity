#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# helper.py

"""
Some helper for parsing smi txt files and extracting the right data.

"""

import numpy as np

def parse_smi(files, t_msg=None, t1=-np.Infinity, t2=+np.Infinity):
    """
    Return parsed files as list of dicts.

    .. note:
        parse_smi uses the x and y coordinate of the left eye.

    Parameters
    ----------
    files : sequence of str
        file names. For every subject one tab separated file.
    t_msg : string
        message that defines the zero point of the time
    t1 : number
        start time that is included
    t2 : number
        stop time that is included

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
            t_zero = None
            data = list()
            msg = list()
            for line in  data_file:
                # skip all commentary
                if line[0] == "#":
                    continue
                parts = line.split("\t")
                if parts[0] == "Time":
                    header_found = True
                    print line
                    # check header
                    if (parts[5] != "L POR X [px]" or
                        parts[6] != "L POR Y [px]"):
                        raise IOError("Header of %s has wrong format." % f)
                    continue
                if parts[1] == "MSG":
                    print line
                    msg_point = (float(parts[0]), parts[3])
                    msg.append(msg_point)
                    if msg_point[1].split(" ")[2].strip() == t_msg:
                        t_zero = msg_point[0]
                        print t_zero
                    continue
                if t_msg is not None:
                    if  t_zero is None:
                        continue
                    time = float(parts[0]) - t_zero
                    if time < t1:
                        continue
                    if time > t2:
                        break
                if parts[1] == "SMP":
                    if not header_found:
                        raise IOError("No header was found before the first line of data.")
                    data_point = (float(parts[5]), # X left eye
                                float(parts[6]), # Y left eye
                                float(parts[0])) # time
                    data.append(data_point)
                    continue
            subjects.append({"data": data, "msg": msg, "file_name": f})
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
            if data.shape[0] == 0:
                continue
            try:
                stop = stops[i]
                # slice intervall
                tmp = data[data[:,2] > start,:]
                tmp = tmp[data[:,2] < stop,:]
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
    slice = gaze_data[gaze_data[:,2] > t - dt/2]
    if slice.shape[0] == 0:
        return slice
    slice = slice[slice[:,2] < t + dt/2]
    return slice

