#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# test_fix_map.py

"""
Test if fix_map and dorr yield the same results.

"""

import unittest

import numpy as np

from .. import dorr

class TestFixMap(unittest.TestCase):

    def setUp(self):
        vec_i_js = np.array([[1, 2, 3],
                             [-1, -0.2, -4],
                             [4, 5, 6]])
        self.stds = np.array([2, 4, 6])
        self.fix_map = dorr.generate_fixation_map_cython(vec_i_js, self.stds)
        self.dorr_fix_map = dorr.generate_fixation_map(vec_i_js, self.stds)

    def test_equal_to_gauss_dorr(self):
        vec_i_js = np.array([[2, 4, 6],])
        fix_map = dorr.generate_fixation_map(vec_i_js, self.stds)
        vec = np.array([0, 0, 0])
        self.assertAlmostEqual(fix_map(vec), dorr.gaussian(vec, vec_i_js[0],
                                                           self.stds))

    def test_equal_to_gauss_cython(self):
        vec_i_js = np.array([[2, 4, 6],])
        fix_map = dorr.generate_fixation_map_cython(vec_i_js, self.stds)
        vec = np.array([0, 0, 0])
        self.assertAlmostEqual(fix_map(vec), dorr.gaussian(vec, vec_i_js[0],
                                                           self.stds))

    def test_equality(self):
        nn = 5
        vecs = np.random.random(nn * 3)
        vecs.shape = (nn, 3)
        for vec in vecs:
            self.assertAlmostEqual(self.fix_map(vec), self.dorr_fix_map(vec))

if __name__ == '__main__':
    unittest.main()

