#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# nss.py

"""
Caculating the coherence values.

"""

from __future__ import absolute_import

import time

import numpy as np

from . import dorr
from . import helper

def nss(subjects, t, dt, stds, dt_max, n_reference,
        method="xy-population", n_norm=10000, population=None,
        screen_res=(1600, 1200), velocity=False, method_velocity="gamma"):
    """
    calculates the normalized scanpath value for a given time t.

    Parameters
    ----------
    subjects : sequence
        sequence of np.arrays for every subject one np.array
    t : float
        point in time
    dt : float
        width of the time window
    stds : sequence of floats
        standard deviations for x, y and t or r, phi and t if velocity=True
    dt_max : float
        maximal difference between t and a valid sample of a subject.
    n_reference : integer
        number of reference subjects, that should be used. Uses the next
        n_reference subjects as reference.
    method : {"xy-estimation", "xy-population", "xy-grid", "xyt-grid",
        "xy-plane"}
        which normalization method should be used?
    n_norm : integer
        number of norm samples used for the normalization method.
    population : np.array
        basic population used to normalize the fixation map. This is only used
        in xy-population normalization.
    screen_res : tuple
        (x_res, y_res) the horizontal and vertical resolution of the screen
        used to collect the gaze data. This values are only used in grid
        normalization.
    velocity : bool
        if velocity is True functions for velocity_map will be used in stead of
        fixation_map

    Returns
    -------
    (nss_values, quality_values) : (sequence, sequence)
        individual nss_values and quality values for all subjects
    quality_value : integer
        gives the number of data points used of one subject

    """
    slices = list()
    for gaze in subjects:
        slice_ = helper.slice_time_window(gaze, t, dt)
        # remove invalid gaze data (marked with NaN)
        if len(slice_) > 0:
            slice_ = slice_[np.logical_not(np.isnan(slice_[:,0])),:]
        if len(slice_) > 0:
            slice_ = slice_[np.logical_not(np.isnan(slice_[:,1])),:]
        slices.append(slice_)
    del slice_
    # remove invalid gaze data (marked with NaN)
    if len(population) > 0:
        population = population[np.logical_not(np.isnan(population[:, 0])),:]
    if len(population) > 0:
        population = population[np.logical_not(np.isnan(population[:, 1])),:]
    quality_values = [len(slice_) for slice_ in slices]
    nss_values = list()
    for i, subject in enumerate(subjects):
        start_time = time.time()
        if np.min(np.abs(subject[:, 2] - t)) > dt_max:
            nss_values.append(np.NAN)
            continue
        point_subject = subject[np.argmin(np.abs(subject[:, 2] - t))]
        x_subject, y_subject, t_subject = point_subject
        idx_right = i + n_reference + 1
        if idx_right > len(subjects):
            reference_slices = (slices[i+1:] +
                                slices[:idx_right-len(subjects)])
        else:
            reference_slices = slices[i+1:idx_right]
        joint_slices = np.concatenate(reference_slices, axis=0)
        if velocity:
            fix_map = dorr.generate_velocity_map(joint_slices, stds,
                                                 method=method_velocity)
        else:
            fix_map = dorr.generate_fixation_map_cython(joint_slices, stds)
            #fix_map = dorr.generate_fixation_map(joint_slices, stds)
        norm_sample = generate_norm_sample(t_subject, dt, method, population,
                                           n_norm, screen_res)
        nss_map = dorr.generate_nss_map(fix_map, norm_sample)
        nss_values.append(nss_map(np.array([x_subject, y_subject, t_subject])))
        #print("Iteration for nss value need: %f sec" % (time.time() - start_time))
    return (nss_values, quality_values)

def generate_norm_sample(t, dt, method="xy-population", population=None,
                         n=10000, screen_res=(1600, 1200)):
    """
    Generate a random norm sample out of population.

    The norm sample is sampled from x, y coordinates of the population and is
    uniform in time around the point in time t in the time window dt.

    Parameters
    ----------
    t : float
        point in time
    dt : float
        width of time window
    method : {"xy-estimation", "xy-population", "xy-grid", "xyt-grid",
        "xy-plane"}
        which normalization method should be used?
    n : integer
        number of samples in the returned norm sample or string {"n_xXn_y",
        "n_xXn_yXn_time"}
    population : np.array
        numpy array with x, y, t coordinates of the basic population. This is
        only used in xy-population normalization.
    screen_res : tuple
        (x_res, y_res) the horizontal and vertical resolution of the screen
        used to collect the gaze data. This values are only used in grid
        normalization.

    """
    if method == "xy-estimation":
        std_x, std_y = np.std(population[:, :2], axis=0)
        mean_x, mean_y = np.mean(population[:, :2], axis=0)
        x = np.random.normal(mean_x, std_x, (n, 1))
        y = np.random.normal(mean_y, std_y, (n, 1))
        times = t * np.ones((n, 1))
        norm_sample = np.concatenate((x, y, times), axis=1)
        return norm_sample
    elif method == "xy-population":
        idx = np.random.random_integers(0, len(population)-1, n)
        times = t * np.ones((n, 1))
        norm_sample = np.concatenate((population[idx, :2], times), axis=1)
        return norm_sample
    elif method == "xyt-grid":
        try:
             n_x, n_y, n_time = [int(nn) for nn in n.split("X")]
        except ValueError:
            raise ValueError("method xyt-grid assumes n='n_xXn_yXn_time', e. g. '120X72X10' as a string literal")
        offset_x = np.random.uniform(0.0, screen_res[0]/n_x)
        offset_y = np.random.uniform(0.0, screen_res[1]/n_y)
        x = np.tile(np.repeat(np.linspace(0, screen_res[0], n_x), n_y), n_time)
        x.shape = (n_x*n_y*n_time, 1)
        x += offset_x
        y = np.tile(np.tile(np.linspace(0, screen_res[1], n_y), n_x), n_time)
        y.shape = (n_x*n_y*n_time, 1)
        y += offset_y
        times = np.repeat(np.linspace(t - dt/2., t + dt/2., n_time), n_x*n_y)
        times.shape = (n_x*n_y*n_time, 1)
        norm_sample = np.concatenate((x, y, times), axis=1)
        return norm_sample
    elif method == "xy-grid":
        try:
             n_x, n_y = [int(nn) for nn in n.split("X")]
        except ValueError:
            raise ValueError("method xy-grid assumes n='n_xXn_y', e. g. '120X72' as a string literal")
        offset_x = np.random.uniform(0.0, screen_res[0]/n_x)
        offset_y = np.random.uniform(0.0, screen_res[1]/n_y)
        x = np.repeat(np.linspace(0, screen_res[0], n_x), n_y)
        x.shape = (n_x*n_y, 1)
        x += offset_x
        y = np.tile(np.linspace(0, screen_res[1], n_y), n_x)
        y.shape = (n_x*n_y, 1)
        y += offset_y
        times = np.repeat(t, n_x*n_y)
        times.shape = (n_x*n_y, 1)
        norm_sample = np.concatenate((x, y, times), axis=1)
        return norm_sample
    elif method == "xy-plane":
        x = np.random.uniform(0, screen_res[0], n)
        y = np.random.uniform(0, screen_res[1], n)
        times = t * np.ones(n)
        norm_sample = np.concatenate((x, y, times), axis=1)
        return norm_sample
    else:
        raise ValueError("{method} is not supported.".format(method=method))

