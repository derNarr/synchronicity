#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# job_sim.py

"""
Defines a specific job, that should be simulated.

"""

from __future__ import division

import time
import sys

sys.path.append("..")

from synchronicity.simulate import run_simulation, init_simulation

start = int(sys.argv[1])
stop = int(sys.argv[2])


# r_param: 0.0002 .. 0.00001
# phi_param: 0.5 .. 2
run_simulation("ducks_boat_20.pickle",
               "data_sim_location_ducks_boat_20_start%i_stop%i_%s.txt"
               % (start, stop, time.strftime("%Y%m%d_%H%M%S")),
               ts=[x*40000 for x in range(start, stop)],
               #dts=(225000,),
               dts=(20000,),
               n_refs=(19,),
               methods=("xy-population",),
               n_norms=(1000,),
               #dt_max_velocity=None,
               #setup=((1280, 720), (50, 50, 1/60*1000000),
               #           2*1/60*1.1*1000000))
               dt_max_velocity=5000,
               setup=((1280, 720), (0.00010, 0.8, 1/50*1000000),
                          1/50*1000000),
                          #2*1/20*1.1*1000000),
               method_velocity="clip")

#init_simulation(pickle_file="ducks_boat_20.pickle",
#                folder="./gaze_data_ducks_boat/",
#                video="ducks_boat",
#                format="coord")

# 0.0001 ist schon ganz gut
# 0.00001 even better
# 0.000001 still good
# 0.0000001 no so good?

