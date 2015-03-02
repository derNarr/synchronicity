#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# dorr_c.pyx

"""
Fast version to generate fixation map as in dorr.

The solution in dorr.py is the reference and if there is a difference in the
results the pure python version is right ;)

"""

import numpy as np

cimport numpy as np
DTYPE = np.float

def fix_map(np.ndarray vec not None, np.ndarray vec_i_js not None, np.ndarray
            stds not None):
    cdef np.ndarray n_vec = vec / stds
    cdef np.ndarray n_vec_means = vec_i_js / stds
    cdef np.ndarray dists = np.sum((n_vec - n_vec_means)**2, axis=1)
    return np.sum(np.exp(-dists*0.5))

