"""Python implementation of DYNMOD

References
----------
.. [1] Fread, D.L., 1973, A dynamic model of stage-discharge
   relations affected by changing discharge: NOAA Technical
   Memorandum NWS HYDRO-16, 55 p.
   http://repository.library.noaa.gov/view/noaa/13480

"""

# import logging

import numpy as np
from scipy.optimize import newton

import dynrat
from dynrat import GRAVITY


# module-level logger
logger = dynrat.logger.getChild(__name__)


class QSolver:
    """Iterative solver for discharge using stage time series.

    Parameters
    ----------
    sect : Sect
        Provides cross section area and top width
    frict : Frict
        Provides Manning's n
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

        self.logger = logger.getChild(self.__class__.__name__)

    def _dhs(self, h, h_prime):
        return (h - h_prime) / self._time_step

    def _f(self, q, l2, l3, l4, l5, l6):
        """Zero function.

        This private method is meant to be used internally during the
        iterative solution of `q`. `l2`, `l3`, `l4`, `l5`, and `l6` do
        not need to be computed for every iteration.
        """

        l0 = self._L0(q, l3, l4, l5, l6)

        f = q - l2 * l0**(1 / 2)

        self.logger.debug("f computed {}".format(f))

        if not np.isfinite(f):
            self.logger.error(
                "f computed a non-finite value")
            raise RuntimeError("Non-finite value computed")

        if np.iscomplex(f):
            self.logger.error("f computed a complex value")
            raise RuntimeError("Complex value computed")

        return f

    def _f_prime(self, q, l2, l3, l4, l5, l6):
        """Derivative (with respect to q) of the zero function.

        This private method is meant to be used internally during the
        iterative solution of `q`. `l2`, `l3`, `l4`, `l5`, and `l6` do
        not need to be computed for every iteration.
        """

        l0 = self._L0(q, l3, l4, l5, l6)
        l1 = self._L1(q, l4, l5, l6)

        f_prime = 1 - 0.5 * l2 * l1 / l0**(1 / 2)

        self.logger.debug("f_prime computed {}".format(f_prime))

        if not np.isfinite(f_prime):
            self.logger.error(
                "f_prime computed a non-finite value")
            raise RuntimeError("Non-finite value computed")

        if np.iscomplex(f_prime):
            self.logger.error("f_prime computed a complex value")
            raise RuntimeError("Complex value computed")

        return f_prime

    def _K(self, h, h_prime):

        dh = h - h_prime

        if dh == 0:
            k = 5/3
        else:
            top_width = self._sect.top_width(h)
            wetted_perimeter = self._sect.wetted_perimeter(h)
            wetted_perimeter_prime = self._sect.wetted_perimeter(h_prime)
            area = self._sect.area(h)
            dPdh = (wetted_perimeter - wetted_perimeter_prime)/dh
            k = 5 / 3 - 2 / 3 * (area / (top_width * wetted_perimeter)) * dPdh

        if k < 0:
            self.logger.warning("K = {} < 0".format(k))

        return k

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
        dhs = self._dhs(h, h_prime)

        l4 = area * dhs / k

        return l4

    def _L5(self, h, h_prime):

        k = self._K(h, h_prime)
        top_width = self._sect.top_width(h)
        area = self._sect.area(h)
        dhs = self._dhs(h, h_prime)

        l5 = (1 - 1 / k) * top_width * dhs / (GRAVITY * area**2) \
            - 1 / (GRAVITY * area * self._time_step)

        return l5

    def _L6(self, h):

        top_width = self._sect.top_width(h)
        area = self._sect.area(h)

        return -2 / 3 * (self._bed_slope * top_width) \
            / (self._slope_ratio**2 * GRAVITY * area**3)

    def q_solve(self, h, h_prime, q_prime, q0=None):
        """Iteratively solves for discharge

        Parameters
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

        root, r = newton(
            lambda q: self._f(
                q, l2, l3, l4, l5, l6),
            q0,
            lambda q: self._f_prime(
                q, l2, l3, l4, l5, l6),
            full_output=True, tol=tol, disp=False)

        if not r.converged:
            self.logger.error("dynmod solver failed to converge after "
                              + "{} iterations".format(r.iterations))
            raise RuntimeError("dynmod zero function failed to converge")
        else:
            self.logger.debug("Converged to value " +
                              "{} after {} iterations".format(root,
                                                              r.iterations))

        return root

    def zero_func(self, h, h_prime, q, q_prime):
        """Iterative solution zero function


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

        Notes
        -----

        Computes the zero function (eq. 15 of [1]_).

        """

        l2 = self._L2(h)
        l3 = self._L3(q_prime, h_prime)
        l4 = self._L4(h, h_prime)
        l5 = self._L5(h, h_prime)
        l6 = self._L6(h)

        return self._f(q, l2, l3, l4, l5, l6)
