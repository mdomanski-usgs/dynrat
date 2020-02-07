"""Python implementation of DYNMOD

References
----------
.. [1] Fread, D.L., 1973, A dynamic model of stage-discharge
   relations affected by changing discharge: NOAA Technical
   Memorandum NWS HYDRO-16, 55 p.
   http://repository.library.noaa.gov/view/noaa/13480

"""

import numpy as np
from scipy.optimize import newton


GRAVITY = 32.2


class Frict:
    """Linearly interpolates Manning's n

    `stage` and `roughness` must be one-dimensional and have two elements
    or more. `stage` must be sorted in ascending order.

    Parameters
    ----------
    stage : array_like
        Water surface elevations
    roughness : array_like
        Manning's n values

    """

    def __init__(self, stage, roughness):

        self._stage = np.array(stage)
        self._roughness = np.array(roughness)

        if self._stage.ndim != 1:
            raise ValueError("stage must be one-dimensional")

        if self._stage.size < 2:
            raise ValueError("stage must at least have two elements")

        if not np.alltrue(np.diff(stage) >= 0):
            raise ValueError("stage must be sorted in ascending order")

        if self._roughness.ndim != 1:
            raise ValueError("roughness must be one-dimensional")

        if self._roughness.size < 2:
            raise ValueError("roughness must at least have two elements")

        if self._stage.size != self._roughness.size:
            raise ValueError("stage and roughness must have the same size")

    def roughness(self, stage):
        """Computes Manning's n for a particular elevation of the
        water surface.

        Parameters
        ----------
        stage : array_like
            Water surface elevation

        Returns
        -------
        float or ndarray
            Manning's n

        """

        return np.interp(stage, self._stage, self._roughness)


class Sect:

    def area(self, stage):
        pass

    def top_width(self, stage):
        pass


class QSolve:
    """Iterative solver for discharge using stage time series.

    Parameters
    ----------
    sect : Sect
        Provides cross section area and top width as a function of
        stage.
    frict : Frict
        Provides Manning's n as a function of stage.
    bed_slope : float
        Bed slope of channel
    slope_ratio : float
        Ratio of the channel bed slope to an average wave slope.
    time_step : float
        Time series time step, in seconds.

    """

    def __init__(self, sect, frict, bed_slope, slope_ratio, time_step):

        self._bed_slope = bed_slope
        self._frict = frict
        self._sect = sect
        self._slope_ratio = slope_ratio
        self._time_step = time_step

    def _dh(self, h, h_prime):
        return (h - h_prime) / self._time_step

    @classmethod
    def _f(cls, q, l2, l3, l4, l5, l6):
        """Zero function.

        This private method is meant to be used internally during the
        iterative solution of `q`. `l2`, `l3`, `l4`, `l5`, and `l6` do
        not need to be computed for every iteration.
        """

        l0 = cls._L0(q, l3, l4, l5, l6)

        return q - l2 * l0**(1 / 2)

    @classmethod
    def _f_prime(cls, q, l2, l3, l4, l5, l6):
        """Derivative (with respect to q) of the zero function.

        This private method is meant to be used internally during the
        iterative solution of `q`. `l2`, `l3`, `l4`, `l5`, and `l6` do
        not need to be computed for every iteration.
        """

        l0 = cls._L0(q, l3, l4, l5, l6)
        l1 = cls._L1(q, l4, l5, l6)

        return 1 - 0.5 * l2 * l1 / l0**(1 / 2)

    def _K(self, h, h_prime):

        top_width_prime = self._sect.top_width(h_prime)
        top_width = self._sect.top_width(h)
        area = self._sect.area(h)

        dh = h - h_prime

        # minimum dh value for computing the derivative of
        # top with with respect to stage
        if dh == 0:
            dh = 0.001

        dBdh = (top_width - top_width_prime) / dh

        return 5 / 3 - 2 / 3 * (area / top_width**2) * dBdh

    @staticmethod
    def _L0(q, l3, l4, l5, l6):

        return l3 + l4 / q + l5 * q + l6 * q**2

    @staticmethod
    def _L1(q, l4, l5, l6):

        return -l4 / q**2 + l5 + 2 * l6 * q

    def _L2(self, h):

        area = self._sect.area(h)
        top_width = self._sect.top_width(h)
        n = self._frict.roughness(h)

        hydraulic_depth = area / top_width

        return 1.486 * area * hydraulic_depth**(2 / 3) / n

    def _L3(self, q_prime, h_prime):

        area_prime = self._sect.area(h_prime)

        return self._bed_slope + \
            2 / 3 * self._bed_slope / self._slope_ratio**2 \
            + q_prime / (GRAVITY * area_prime * self._time_step)

    def _L4(self, h, h_prime):

        area = self._sect.area(h)
        k = self._K(h, h_prime)
        dh = self._dh(h, h_prime)
        return area * dh / k

    def _L5(self, h, h_prime):

        k = self._K(h, h_prime)
        top_width = self._sect.top_width(h)
        area = self._sect.area(h)
        dh = self._dh(h, h_prime)

        return (1 - 1 / k) * top_width * dh / (GRAVITY * area**2) \
            - 1 / (GRAVITY * area * self._time_step)

    def _L6(self, h):

        top_width = self._sect.top_width(h)
        area = self._sect.area(h)

        return -2 / 3 * (self._bed_slope * top_width) \
            / (self._slope_ratio**2 * GRAVITY * area**3)

    def q_solve(self, h, h_prime, q_prime, q0=None):
        """Iteratively solves for discharge

        Paramters
        ---------
        h : float
            Stage of current time step
        h_prime : float
            Stage of previous time step
        q_prime : float
            Discharge of previous time step
        q0 : {float, None}, optional
            Initial estimate of q (the default is, None, which uses
            `q_prime` as an initial estimate).

        """

        l2 = self._L2(h)
        l3 = self._L3(q_prime, h_prime)
        l4 = self._L4(h, h_prime)
        l5 = self._L5(h, h_prime)
        l6 = self._L6(h)

        # convergence tolerance
        tol = 1.0  # cfs

        if q0 is None:
            q0 = q_prime

        q = newton(
            lambda q: self._f(
                q, l2, l3, l4, l5, l6),
            q0,
            lambda q: self._f_prime(
                q, l2, l3, l4, l5, l6),
            tol=tol)

        return q

    def zero_func(self, h, h_prime, q, q_prime):
        """Iterative solution zero function

        Computes the zero function (eq. 15 of [1]_).

        Parameters
        ----------
        h : float
            Stage of current time step
        h_prime : float
            Stage of previous time step
        q : float
            Discharge of current time step
        q_prime : float
            Discharge of previous time step

        """

        l2 = self._L2(h)
        l3 = self._L3(q_prime, h_prime)
        l4 = self._L4(h, h_prime)
        l5 = self._L5(h, h_prime)
        l6 = self._L6(h)

        return self._f(q, l2, l3, l4, l5, l6)
