#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# simulate.py

"""
A simulation which calculates coherence values for different parameter sets.

.. note::
    The population consists of all subjects, not only the subset.

"""

from __future__ import division
from __future__ import absolute_import

import os
import pickle
import time

import numpy as np
from scipy import stats

from . import nss
from . import helper

def init_simulation(pickle_file, folder, video, format="smi"):
    """
    Construct all constant stuff and pickle it.

    Parameters
    ----------
    pickle_file: string
        pickle file storing the gaze data
    folder : string
        folder with the eye tracking raw data
    video : string
        video string used in smi message (msg)
    format : {"smi", "coord"}
        defines how the video should be parsed

    """
    if format == "smi":
        files = [folder + "/" + x for x in os.listdir(folder)]
        subjects = helper.parse_smi(files)
        gaze_data = helper.extract_video_data(subjects, video)
    elif format == "coord":
        files = [folder + "/" + f for f in os.listdir(folder)]
        gaze_data = helper.parse_coord(files)

    print("n_subjects: %i" % len(gaze_data))
    population = np.concatenate(gaze_data, axis=0)
    with open(pickle_file, "wb") as pfile:
        obj = (gaze_data, population)
        pickle.dump(obj, pfile)


def run_simulation(pickle_file, data_file, ts, dts, n_refs, methods, n_norms,
                   setup=((1280, 720), (50, 50, 1/60/2*1000000),
                          1/60*1.1*1000000), dt_max_velocity=None, method_velocity="clip"):
    """
    Unpickle init values and run simulation.

    Parameters
    ----------
    pickle_file: string
        pickle file storing the gaze data
    data_file : string
        data file to store the results
    ts : sequence of floats
        points in time where the coherence value should be
        evaluated.
    dts : sequence of floats
        width of time windows
    n_refs : sequence of integers
        number of reference subjects
    methods : sequence of strings
        normalization method
    n_norms : sequence of integers
        number of norm samples
    setup : tuple of tuples
        (screen_res, stds, dt_max)
    dt_max_velocity : *None* or float
        indicates if the velocity should be used instead of the location and
        sets the maximal time difference that is included into the velocity
        array. When dt_max_velocity is None locations are used.
    method_velocity : {"clip", "heavyside", "gamma"}

    """
    screen_res, stds, dt_max = setup
    SIGMA_X, SIGMA_Y, SIGMA_T = stds

    print("load parameters...")
    with open(pickle_file, "rb") as pfile:
        subjects, population = pickle.load(pfile)
    n_subjects = len(subjects)
    print("screen_res: %i, %i" % screen_res)
    print("standard deviations: %f, %f, %f" % stds)
    print("dt_max: %f" % dt_max)
    print("n_subjects: %i" % n_subjects)
    velocity = False
    if dt_max_velocity is not None:
        velocity = True
        print("\ncalculate velocities...")
        velocity_subjects = list()
        for gaze_data in subjects:
            velocity_subjects.append(helper.velocity(gaze_data,
                                                     dt_max_velocity))
        velocity_population = np.concatenate(velocity_subjects, axis=0)
        print("WARNING: cannot use given population; " +
              "recreated population out of subjects.")
        subjects = velocity_subjects
        population = velocity_population
        if method_velocity == "heavyside":
            subjects = [subject[subject[:, 0] >= stds[0], :] for subject in subjects]
            population = population[population[:, 0] >= stds[0], :]
        print("...done")
    print("\nstart simulation...")
    with open(data_file, "a") as dfile:
        quality_header = "qf%i\t"*n_subjects % tuple(range(n_subjects))
        nss_header = "nss%i\t"*n_subjects % tuple(range(n_subjects))
        dfile.write("gaze_file\tt\tnss_mean\tnss_nanmean\tn_nan\tn_subjects\tn_reference\tmethod\tdt\tn_norm\tSIGMA_X\tSIGMA_Y\tSIGMA_T\tdt_max\tdt_max_velocity\t%s%stotal_time\n" % (quality_header, nss_header))
        for t in ts:
          for dt in dts:
            for n_reference in n_refs:
              for method in methods:
                for n_norm in n_norms:
                    print("t/dt/n_reference/method/n_norm")
                    print("%f/%f/%i/%s/%s" % (t, dt, n_reference, method,
                                              str(n_norm)))
                    start_time = time.time()
                    nss_values, quality_values  = nss.nss(subjects, t, dt,
                                         stds, dt_max,
                                         n_reference, method, n_norm,
                                         population, screen_res,
                                         velocity, method_velocity)
                    end_time = time.time()
                    total_time = end_time - start_time
                    print("time needed in sec: %f and in min: %i" %
                          (total_time, int(total_time/60)))
                    quality = "%i\t"*n_subjects % tuple(quality_values)
                    nss_subjects = "%e\t"*n_subjects % tuple(nss_values)
                    result = "%s\t%e\t%e\t%e\t%i\t%i\t%i\t%s\t%e\t%s\t%f\t%f\t%f\t%i\t%s\t%s%s%f\n" %\
                                (pickle_file, t, np.mean(nss_values),
                                stats.nanmean(nss_values),
                                np.sum(np.isnan(nss_values)), n_subjects,
                                n_reference, method, dt, str(n_norm), SIGMA_X, SIGMA_Y,
                                SIGMA_T, dt_max, str(dt_max_velocity), quality,
                                nss_subjects, total_time)
                    print(result)
                    dfile.write(result)


if __name__ == "__main__":
    init_simulation(pickle_file="sim_para_breite_strasse.pickle",
                    folder="../data/dorr/gaze/natural_movies_gaze",
                    video="breite_strasse",
                    format="coord")
#    run_simulation("sim_para_bbt_21.pickle",
#                   "data_simulation_%s.txt" % time.strftime("%Y%m%d_%H%M%S"),
#                   ts=(5*60*1000000,),
#                   dts=(67000,),
#                   n_refs=(19,),
#                   methods=("xy-population",),
#                   n_norms=(100, 1000, 10000, 100000)*50)


