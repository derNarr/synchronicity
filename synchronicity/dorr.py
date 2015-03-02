#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# dorr.py


"""
Implementation of the NSS algorithm described in doi: 10.1167/10.10.28 Journal
of Vision August 26, 2010 vol. 10 no. 10 article 28.

General Method
--------------
With the leave one out paradigm a Normalized Scanpath Saliency (NSS) map is
constructed for every observer (and every point in time) out of all other
observers. Calculate the saliency for this one observer for this point
in time. Repeat this procedure for every observer and add the calculated
saliences.

In order to calculate the NSS map you have to::
    1. calculate the spatiotemporal Gaussian distribution for every
        spatiotemporal point
    2. sum this Gaussian distributions to a fixation map
    3. normalize these fixation map to mean zero and standard deviation one

Generalisations
---------------
Instead of a spatiotemporal Gaussian distribution other distributions are
defined in this file and can be used. This is especially important for the use
in order to calculate synchronicity.

"""

from __future__ import division
from __future__ import absolute_import

import functools

import numpy as np
import scipy.stats

from . import dorr_c


def gaussian(vec, vec_mean, stds):
    """
    Three dimensional spatiotemporal Gaussian distribution.

    .. warning::
        This formula was altert from the original formula in [1]_.

    Parameters
    ----------
    vec : np.matrix
        The first two values define the location on the screen and the third
        value defines the time. (x, y, t)
    vec_mean : np.matrix
        Vector of one specific observer i and one specific movie j.
    stds : sequence
        Sequence containing all standard deviations for the entries in
        vec_mean, e. g. (SIGMA_X, SIGMA_Y, SIGMA_T)

    References
    ----------
    See formula (2) in [1]_

    """
    std = np.array(stds)
    n_vec = vec / std
    n_vec_mean = vec_mean / std
    dist = float((np.matrix(n_vec - n_vec_mean)) *
                 (np.matrix(n_vec - n_vec_mean)).transpose())
    return np.exp(-dist/2)
    # original formula (2) in [1]_ (which is wrong and was never used in code):
    #dist = float((np.matrix(vec - vec_mean)) *
    #             (np.matrix(vec - vec_mean)).transpose())
    #return np.exp(-dist / (2 * np.sum(variances)))


def kernel_velocity(vec, vec_mean, stds, method="gamma"):
    r"""
    Three dimensional spatio temporal kernel distribution for polar
    coordinates.

    Parameters
    ----------
    vec : np.matrix
        The first two values define the velocity on the screen and the third
        value defines the time. (r, phi, t), phi \in [-pi, pi]
    vec_mean : np.matrix
        Vector of one specific observer i and one specific movie j.
    stds : sequence
        Sequence containing three parameters for the three parts of the kernel,
        the radius, the angle, and the time dependent part and therefore for
        the entries in vec_mean, i. e. (PARAM_R, PARAM_PHI, PARAM_T)
    method : {"gamma", "heavyside"}
        Method used for the r dependency.

    .. note::

        The chi2 distribution used for the r dependency gives weight to the zero
        for mean_rr/PARAM_R < 2 and weight around the mean_rr for
        mean_rr/PARAM_R >= 2.

    References
    ----------
    See formula (2) in [1]_

    """
    param_r, param_phi, param_t = stds
    rr, phi, tt = vec
    mean_rr, mean_phi, mean_tt = vec_mean

    rr_rescaled = rr / param_r
    mean_rr_rescaled = mean_rr / param_r

    # rr -> length distribution
    # using a gamma distribution with \beta = 1 and \alpha = rr_rescaled
    # the rr_rescaled / (0.1 + rr_rescaled) factor garanties a nice behaviour
    # around zero
    if method == "gamma":
        ret_rr = (scipy.stats.gamma.pdf(rr_rescaled, mean_rr_rescaled) *
                rr_rescaled / (0.1 + rr_rescaled))
    elif method == "heavyside":
        if rr >= param_r:
            ret_rr = 1.0
        else:
            return 0.0
    else:
        raise ValueError("method %s not defined" % method)

    # phi -> renormed clipped Gaussian distribution
    # 1/r corrects approximately for the increasing arc
    diff_phi = phi - mean_phi
    if diff_phi < -np.pi:
        diff_phi += 2 * np.pi
    elif diff_phi > np.pi:
        diff_phi -= 2 * np.pi
    ret_phi = scipy.stats.norm.pdf(diff_phi, scale=param_phi)
    # renorm to area of one due to clipping
    ret_phi *= 1 / (1 - 2 * scipy.stats.norm.cdf(- np.pi, scale=param_phi))
    # correct for increasing arc (approximately??) -- don't need that anymore
    #ret_phi *= 1 / (2 * np.pi * mean_rr_rescaled)

    # tt -> Gaussian distribution
    ret_tt = scipy.stats.norm.pdf(tt, loc=mean_tt, scale=param_t)

    return ret_rr * ret_phi * ret_tt


def velocity_map_clip(vec, vec_i_js, stds):
    """
    Very crude way without any interpolation. We give cutoffs and set
    everything to zero beyond the cutoff. If the result is not zero it is one.

    Therefore this is some kind of indication function if we decide to say two
    vectors are the same or different.

    Returns the number of same vectors.

    """
    if vec[0] < stds[0]:
        return 0
    result = np.ones(len(vec_i_js), dtype=int)
    # r
    result[vec_i_js[:, 0] < stds[0]] = 0
    # phi
    d_phis = abs(vec[1] - vec_i_js[:, 1])
    d_phis[d_phis > np.pi] -= 2 * np.pi
    d_phis = abs(d_phis)
    result[d_phis > stds[1]] = 0
    # t
    d_ts = abs(vec[2] - vec_i_js[:, 2])
    result[d_ts > stds[2]] = 0
    return np.sum(result)


def generate_fixation_map(vec_i_js, stds):
    """
    Generate spatiotemporal fixation map.

    Parameters
    ----------
    vec_i_js : list of np.matrix
        Every list entry is a vector of one specific observer i and one
        specific movie j.
    stds : sequence
        Sequence containing all standard deviations for the entries in
        vec_mean, e. g. (SIGMA_X, SIGMA_Y, SIGMA_T)

    .. note:
        The sequence of vec_i_js should not contain any values of the test
        observer.

    Returns
    -------
    fixation_map : function
        function accepting one vector (x, y, t)

    References
    ----------
    See formula (1) in [1]_

    """
    def fixation_map(vec):
        """
        Spatiotemporal fixation map.

        Parameters
        ----------
        vec : np.matrix
            The first two values define the location on the screen and the
            third value defines the time. (x, y, t)

        Returns
        -------
        saliency : float
            not normalized saliency for the point vec.

        """
        return np.sum([gaussian(vec, vec_i_j, stds) for vec_i_j in
                       vec_i_js])
    return fixation_map


def generate_velocity_map(vec_i_js, stds, method):
    """
    Generate spatiotemporal velocity map.

    Parameters
    ----------
    vec_i_js : list of np.matrix
        Every list entry is a vector of one specific observer i and one
        specific movie j. Each vector is given in polar coordinates i. e. (r,
        phi, t)
    stds : sequence
        Sequence containing all standard deviations for the entries in
        vec_mean, e. g. (SIGMA_R, SIGMA_PHI, SIGMA_T)

    .. note:
        The sequence of vec_i_js should not contain any values of the test
        observer.

    Returns
    -------
    fixation_map : function
        function accepting one vector (x, y, t)

    References
    ----------
    See formula (1) in [1]_

    """
    if method == "clip":
        velocity_map = functools.partial(velocity_map_clip, vec_i_js=vec_i_js, stds=stds)
    else:
        def velocity_map(vec):
            """
            Spatiotemporal velocity map.

            Parameters
            ----------
            vec : np.matrix
                The first two values define the velocity on the screen and the
                third value defines the time. (r, phi, t)

            Returns
            -------
            saliency : float
                not normalized saliency for the point vec.

            """
            return np.sum([kernel_velocity(vec, vec_i_j, stds, method) for vec_i_j in
                        vec_i_js])
    return velocity_map


def generate_fixation_map_cython(vec_i_js, stds):
    stds = np.array(stds)
    return functools.partial(dorr_c.fix_map, vec_i_js=vec_i_js, stds=stds)
generate_fixation_map_cython.__doc__ = generate_fixation_map.__doc__


def generate_nss_map(fixation_map, norm_sample):
    """
    Generate normalized scanpath saliency (NSS) map.

    The NSS map is a normalized version of the fixation map.

    .. warning:
        Results can differ significantly dependent on the distribution of the
        norm_sample. If the norm sample is a uniform distribution over space
        and time, the NSS map might be sensitive to the number of samples used
        for the fixation_map due to the center of screen bias. It is advised to
        use a uniform distribution in time and a samples distribution over all
        positions collected in the experiment.

    Parameters
    ----------
    fixation_map : function accepting one vector
        fixation_map initialized with vec_i_js.
    norm_sample : np.array with shape nx3
        dependent on this vectors the fixation_map will be normalized to mean
        zero and standard deviation one. You should use at least 10000 samples.

    Returns
    -------
    normalized_scanpath_saliency_map : function
        function that accepts one vector and returns the saliency for this
        point.

    References
    ----------
    See formula (3) in [1]_

    """
    salience_norm_sample = [fixation_map(vec) for vec in norm_sample]
    #salience_norm_sample = np.apply_along_axis(fixation_map, 1, norm_sample) #8x slower
    mean = np.mean(salience_norm_sample)
    sd = np.std(salience_norm_sample)
    def nss_map(vec):
        """
        Normalized scanpath saliency (NSS) map.

        The NSS map is a normalized version of the fixation map.

        .. warning:
            Results can differ significantly dependent on the distribution of
            the norm_sample. If the norm sample is a uniform distribution over
            space and time, the NSS map might be sensitive to the number of
            samples used for the fixation_map due to the center of screen bias.
            It is advised to use a samples over all positions collected in the
            experiment to the time t.

        Parameters
        ----------
        vec : np.matrix
            The first two values define the location on the screen and the
            third value defines the time. (x, y, t)

        Returns
        -------
        saliency : float
            normalized saliency at the point vec.

        """
        return (fixation_map(vec) - mean) / sd
    return nss_map

