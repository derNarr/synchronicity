===========================
Coherence and Synchronicity
===========================

Motivation
==========
Model the synchronicity and the coherence of several people watching the same
dynamic scene. Finding points in time where the synchronicity and coherence is
higher than in another point in time.

Creating a measure that measures the synchronicity and coherence for every
point in time (denoted with the index :math:`j`) for a given set of subjects
(denoted with the index :math:`i`).

Data format
===========
For every person :math:`i` there is a series of gaze points (:math:`x_{ij}`,
:math:`y_{ij}` coordinates in deg or pix) for several points in time
(:math:`t_{ij}`).

From the positions we can calculate the velocity for a given subject :math:`i`
with a simple difference calculation.

.. math::

    t_{jv} = t_j + \frac{t_{j+1} - t_j}{2}

    v_{jx} = \frac{x_{j+1} - x_j}{t_{j+1} - t_j}

    v_{jy} = \frac{y_{j+1} - y_j}{t_{j+1} - t_j}

We might want to transorm these velocities in cartesian coordinates into
velocities in polar coordinates.

.. math::

    v_r = \sqrt{v_x^2 + v_y^2}

    v_\phi = \text{tan}^{-1}(v_y / v_x)

The number of (valid) points in time per subject can differ. Especially for
every given time :math:`t` there is no xy-coordinate for every subject.


Modelling assumptions
=====================
We assume for every given valid xy-coordinate that the person processed the
information at this coordinate and around this coordinate, where the
distribution in space is approximately normal distributed with standard
deviations :math:`\sigma_x` and :math:`\sigma_y`. These normal distribution
models the intentionally processed voveal information and the uncertainty of
the eye tracker in space.

Additionally we model processed information in time as another independent
Gaussian distribution with standard deviation :math:`\sigma_t`. These
models the uncertainty of the eye tracker in time and the fact that even in
a dynamic scene looking at the same point in slightly different points in
time results in a similar information.

We do not model any features of the dynamic scenes. Therefore this measure
does not account for cuts, rapid changes etc. in the dynamic scene. It only
models the behavioral gaze data of the subjects.

The resulting multivariate Gaussian distribution [wiki_mnorm]_ is

.. math::
    G_{ij}(\vec{x}) = \frac{1}{(2\pi)^{3/2}|\boldsymbol\Sigma|^{1/2}}
    \exp\left(-\frac{1}{2}(\vec{x}-\vec{\mu})^T {\boldsymbol\Sigma}^{-1}
    (\vec{x}-\vec{\mu}) \right)

with the mean vector :math:`\boldsymbol\mu` and the covariance matrix
:math:`\boldsymbol\Sigma`:

.. math::
    \boldsymbol\mu = \begin{pmatrix} x_{ij} \\ y_{ij} \\ t_{ij} \end{pmatrix},

    \boldsymbol\Sigma = \begin{pmatrix} \sigma_x^2 & 0 & 0 \\ 0 &
    \sigma_y^2 & 0 \\ 0 & 0 & \sigma_t^2 \end{pmatrix}


Saliency Map (Fixation Map)
===========================
In order to obtain a saliency map we can simply superpose all valid gaze
points modelled with the multivariate normal distribution :math:`G_{ij}`.

.. math::
    F(\vec{x}) = \sum_{ij} G_{ij}(\vec{x})

This superposition of normal distributions is highly dependent on the
number of valid gaze data in the region of interest. Additionally by
construction it yields higher values for a greater number of subjects.


Normalized Saliency Map
=======================
In order to account for the varying number of valid gaze data, we normalize
the saliency map :math:`F(\vec{x})`. In the end we want to have a
normalized saliency map :math:`N(\vec{x}, t)` with the properties, that for a
given point in time :math:`t` random gaze data :math:`\rho(x, y)` yields a mean of
zero and a standard deviation of one.

.. math::
    N(\vec{x}, t) = \frac{F(\vec{x}) - \text{Mean}_t(F(\vec{x}))}
    {\sqrt{\text{Var}_t(F(\vec{x}))}}

    N(\vec{x}, t) = \frac{F(\vec{x}) - \int \rho(x, y) F(x, y, t) dx dy}
    {\sqrt{\int \rho(x, y) F^2(x, y, t) dx dy - (\int \rho(x, y) F(x, y, t)
    dx dy)^2}}


Random Gaze Data
================
There are two ways of defining randomness in positional gaze data. We
prefer the human based population approach, but in computer science a grid
based approach is also common. The spacial random gaze distribution is
denoted :math:`\rho(x, y)`. And has the property of a density, therefore
:math:`\int \rho(x, y) dx dy = 1`.

Grid based
----------
We define random gaze data as all possible positions within the resolution
of the dynamic scene (e. g. screen resolution, or video resolution).
Therefore we assume uniform distributed gaze data within the screen.

Human based population
----------------------
The marginal spacial distribution of all collected gaze data in the
experimental setting approximates the underling random gaze distribution.

Estimation based
----------------
Estimate some :math:`\rho(x, y)` from the marginal spacial distribution e.
g. a two dimensional Gaussian distribution.


Synchronicity and Coherence Measures
====================================
With normalized saliency maps we can apply a cross validation (rotation
estimation) method [wiki_cross]_ to generate synchronicity or coherence
measures :math:`C(t)` for a point in time :math:`t`. Therefore we calculate for
every valid gaze point :math:`x_{ij}` within a narrow time slice
:math:`\Delta_t` a normalized saliency value and take the mean.

.. math::
    C(t) = \text{Mean}_{\forall \vec{x}_{ij} \text{ with } t-\Delta_t/2 < t_{ij} <
    t+\Delta_t/2} (N_{\hat{i}}(\vec{x}_{ij}, t))

The normalized saliency map :math:`N_{\hat{i}}` is constructed from a
number of reference subjects and does not contain the gaze data of the
subject :math:`i`.

You can apply K-fold cross validation or the special case of leave-one-out
cross validation.

From this time dependent synchronicity or coherence measure you can calculate a
mean synchronicity respectively coherence for a given type of dynamic scenes.

.. math::
    C = \text{Mean}(C(t))


Missing Data
============

Reasons for Missing Data
------------------------
The eye tracker gives the positions where the line of sight of the eye
intersects the plane of the screen. The synchronicity or coherence value should
represent the coherent information collection over several subjects. Therefore
subjects that did a blink (have their eyes shut) or do a saccade i. e. very
fast eye movement should be excluded from the analysis in the moments where
there did the blink or the saccade. This results in a sparsening of the scan
paths for each subjects but on the other hand increases the importance and
meaning of the remaining data points.

The algorithm must deal with this sparse scan paths in an appropriate way.

Dealing with Missing Data
-------------------------

Propagate Missing Data
^^^^^^^^^^^^^^^^^^^^^^
The most strict approach is to exclude all points in time where one or more
subjects did not have valid gaze data. This might result in high numbers an
missing data in the synchronicity or coherence value.

Take what you get
^^^^^^^^^^^^^^^^^
An alternative approach takes all valid gaze data for the point in time and
calculates for this the synchronicity or coherence value. The subjects that do
not have a valid data point should be still used as reference subjects. The
number of reference subjects could be used as a quality factor. This might lead
to wrong synchronicity or coherence values if the synchronicity or coherence
estimation is biased by the number of subjects.

Fixed number of subjects
^^^^^^^^^^^^^^^^^^^^^^^^
Calculating the minimum of valid subjects and use this number of subjects for
all points in time. When for a given point in time more then the minimum number
of subjects have valid gaze points. Randomly sample from this subjects (maybe
several times and take the mean). This deals with the problem of a biased
estimation, but does not take the full power of data into account. (Or becomes
computational very costly.)


References
==========
.. [wiki_mnorm] Multivariate Normal Distribution (http://en.wikipedia.org/wiki/Multivariate_normal_distribution)
.. [wiki_cross] Cross-validation (statistics) (http://en.wikipedia.org/wiki/Cross-validation_%28statistics%29)

