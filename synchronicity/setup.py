#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# setup.py

"""
Compile cython files.

"""

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy as np

ext_modules = [Extension("dorr_c",
                         ["dorr_c.pyx"],
                         include_dirs=[np.get_include()])]

setup(
  name = 'fast fixation map',
  cmdclass = {'build_ext': build_ext},
  ext_modules = ext_modules
)

