#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# create_animation.py

from __future__ import division

import numpy as np
import pickle
import sys

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import animation

sys.path.append("..")

from helper import random_uniform_sample
from synchronicity import dorr


SCREEN_RESOLUTION = (1680, 1024)
SIGMA_X = SIGMA_Y = 1.2*72 # deg * px/deg
SIGMA_T = 26250 # us
DT = 225000 # us

with open("animation_data.pickle", "r") as f:
    test_subject, references = pickle.load(f)

# make it fast for test purposes
#references = references[:25,]

data_point = test_subject[28,:]
variances = (SIGMA_X**2, SIGMA_Y**2, SIGMA_T**2)
fix_map2 = dorr.generate_fixation_map(references, variances)

samples = random_uniform_sample(10000, SCREEN_RESOLUTION, t=DT/2, dt=DT)
print("start normalizing nss_map...")
nss_map = dorr.generate_normalized_scanpath_saliency_map(fix_map2, samples)
print("nss_map created")
del samples

points = list()
fix_points = list()
while not points:
    samples = random_uniform_sample(1000, SCREEN_RESOLUTION, t=DT/2, dt=DT)
    fix_samples = np.array([fix_map2(sample) for sample in samples])
    for i, fix_sample in enumerate(fix_samples):
        if fix_sample*100 > 1.0:
            points.append(samples[i])
            fix_points.append(fix_sample)
POINTS = np.array(points)
FIX_POINTS = np.array(fix_points)
del samples
del fix_samples
del fix_sample

points2 = list()
nss_points = list()
while not points2:
    samples = random_uniform_sample(1000, SCREEN_RESOLUTION, t=DT/2, dt=DT)
    nss_samples = np.array([nss_map(sample) for sample in samples])
    for i, nss_sample in enumerate(nss_samples):
        if nss_sample*100 > 1.0:
            points2.append(samples[i])
            nss_points.append(nss_sample)
POINTS2 = np.array(points2)
NSS_POINTS = np.array(nss_points)
NSS_POINTS[NSS_POINTS <= 0] = 0
del samples
del nss_samples
del nss_sample

del i
del points
del fix_points
del points2
del nss_points

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
print("globals defined")

def set_title(title):
        ax.set_xlim3d((0, SCREEN_RESOLUTION[0]))
        ax.set_ylim3d((0, DT/1000))
        ax.set_zlim3d((0, SCREEN_RESOLUTION[1]))
        ax.title.set_text(title)
        ax.set_xlabel('screen x [pix]')
        ax.set_ylabel('time [ms]')
        ax.set_zlabel('screen y [pix]')

def animate(i):
    if i == 0:
        print("Gaze Data")
        ax.scatter(data_point[0], data_point[2]/1000, data_point[1], s=125,
                c="red")
        ax.scatter(references[:,0], references[:,2]/1000, references[:,1],
                alpha=0.5, linewidth=0)
        ax.scatter(test_subject[:,0], test_subject[:,2]/1000, test_subject[:,1],
                c="red", alpha=0.5, linewidth=0)
        set_title("Gaze Data")
    elif i < 3*30:
        pass
    elif i == 3*30:
        print("Create Fixation Map")
        ax.clear()
        #ax = fig.add_subplot(111, projection='3d')
        ax.scatter(data_point[0], data_point[2]/1000, data_point[1], s=125, c="red")
        set_title("Create Fixation Map")
    elif i < 3*30 + len(references):
        reference = (references[i-3*30],)
        fix_map = dorr.generate_fixation_map(reference, variances)
        points = list()
        fix_points = list()
        while not points:
            samples = random_uniform_sample(100, SCREEN_RESOLUTION, t=DT/2, dt=DT)
            fix_samples = np.array([fix_map(sample) for sample in samples])
            for i, fix_sample in enumerate(fix_samples):
                if fix_sample*100 > 1.0:
                    points.append(samples[i])
                    fix_points.append(fix_sample)
        points = np.array(points)
        fix_points = np.array(fix_points)

        #ax.plot(test_subject[:,0], test_subject[:,2]/1000, test_subject[:,1], "r-", lw=2)
        ax.scatter(reference[0][0], reference[0][2]/1000, reference[0][1],
                   s=25, c="blue")
        ax.scatter(points[:,0], points[:,2]/1000, points[:,1],
                   s=fix_points*100, alpha=0.5, linewidth=0)
        set_title("Create Fixation Map")
    elif i == 3*30 + len(references):
        print("Fixation Map")
        ax.clear()
        #ax = fig.add_subplot(111, projection='3d')
        ax.scatter(data_point[0], data_point[2]/1000, data_point[1], s=125,
                   c="red")
        ax.scatter(POINTS[:,0], POINTS[:,2]/1000, POINTS[:,1],
                   s=FIX_POINTS*100, alpha=0.5, linewidth=0)
        set_title("Fixation Map")
    elif i < 3*30 + len(references) + 3*30:
        pass
    elif i == 3*30 + len(references) + 3*30:
        print("Fixation Map (scale 0.01)")
        ax.clear()
        #ax = fig.add_subplot(111, projection='3d')
        ax.scatter(data_point[0], data_point[2]/1000, data_point[1], s=125,
                   c="red")
        ax.scatter(data_point[0], data_point[2]/1000, data_point[1], s=125,
                   c="red")
        ax.scatter(POINTS[:,0], POINTS[:,2]/1000, POINTS[:,1], s=FIX_POINTS,
                   alpha=0.5, linewidth=0)
        set_title("Fixation Map (scale 0.01)")
    elif i < 3*30 + len(references) + 6*30:
        pass
    elif i == 3*30 + len(references) + 6*30:
        print("NSS Map")
        ax.clear()
        ax.scatter(data_point[0], data_point[2]/1000, data_point[1], s=125,
                   c="red")
        ax.scatter(POINTS2[:,0], POINTS2[:,2]/1000, POINTS2[:,1],
                   s=NSS_POINTS*100, alpha=0.5, linewidth=0)
        set_title("NSS Map")
    elif i < 3*30 + len(references) + 9*30:
        pass
    elif i == 3*30 + len(references) + 9*30:
        print("NSS Map (scale 0.01)")
        ax.clear()
        ax.scatter(data_point[0], data_point[2]/1000, data_point[1], s=125,
                   c="red")
        ax.scatter(POINTS2[:,0], POINTS2[:,2]/1000, POINTS2[:,1],
                   s=NSS_POINTS, alpha=0.5, linewidth=0)
        set_title("NSS Map (scale 0.01)")
    elif i < 3*30 + len(references) + 12*30:
        pass

def main():
    frames = 3*30 + len(references) + 12*30
    anim = animation.FuncAnimation(fig, animate, frames=frames)
    anim.save("animation.mp4", fps=30, codec="mpeg4", bitrate=2000)

if __name__ == "__main__":
    main()

