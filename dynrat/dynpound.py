"""
References
----------
.. [1] Fread, D.L., 1973, A dynamic model of stage-discharge
   relations affected by changing discharge: NOAA Technical
   Memorandum NWS HYDRO-16, 55 p.
   http://repository.library.noaa.gov/view/noaa/13480

"""

import numpy as np
from scipy.optimize import newton

import dynrat
from dynrat import GRAVITY


logger = dynrat.logger.getChild(__name__)


class Solver:

    def __init__(self, sect, bed_slope, slope_ratio, time_step, c_comp='dkda'):

        self._bed_slope = bed_slope
        self._sect = sect
        self._slope_ratio = slope_ratio
        self._time_step = time_step

        if c_comp not in ['const k', 'k', 'dqda', 'dkda']:
            raise ValueError(
                "Unrecognized celerity computation method: {}".format(c_comp))

        self._c_comp = c_comp

        self.logger = logger.getChild(self.__class__.__name__)

    def _celerity(self, h, h_prime, q, q_prime):

        if self._c_comp == 'const k':

            area = self._sect.area(h)

            k = 1.7

            celerity = k * q/area

        elif self._c_comp == 'k':

            area = self._sect.area(h)

            k = self._K(h, h_prime)

            celerity = k * q/area

        elif self._c_comp == 'dqda':

            min_abs_dq = 1e-9
            dq = q - q_prime
            if dq == 0:
                dq = min_abs_dq
            elif np.abs(dq) < 0:
                dq = np.sign(dq)*min_abs_dq

            area = self._sect.area(h)
            area_prime = self._sect.area(h_prime)
            da = area - area_prime
            min_abs_da = 1e-9
            if da == 0:
                da = min_abs_da
            elif np.abs(da) < 0:
                da = np.sign(da)*min_abs_da

            celerity = dq/da

        elif self._c_comp == 'dkda':

            dh = 0.01

            da = self._sect.area(h + dh/2) - \
                self._sect.area(h - dh/2)

            dk = self._sect.conveyance(h + dh/2) - \
                self._sect.conveyance(h - dh/2)

            celerity = self._bed_slope**(1/2)*dk/da

        return celerity

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

    def zero_func(self, h, h_prime, q, q_prime):

        area = self._sect.area(h)
        area_prime = self._sect.area(h_prime)
        da = area - area_prime

        beta = self._sect.vel_dist_factor(h)

        top_width = self._sect.top_width(h)

        dh = h - h_prime
        dq = q - q_prime

        celerity = self._celerity(h, h_prime, q, q_prime)

        dt = self._time_step

        y_partial = -1/celerity*dh/dt - \
            2/3*self._bed_slope/self._slope_ratio**2

        term_1 = 1/(GRAVITY*area)*dq/dt
        term_2 = beta*(2*q)/(GRAVITY*area**2) * da/dt
        term_3 = (1 - beta*top_width*q **
                  2/(GRAVITY*area**3))*y_partial

        k = self._sect.conveyance(h)
        s_f = (q/k)**2

        f = term_1 - term_2 + term_3 + s_f - self._bed_slope

        if not np.isfinite(f):
            self.logger.error("f computed a non-finite value")
            if not np.isfinite(term_1):
                self.logger.debug("term_1 is not finite")
            if not np.isfinite(term_2):
                self.logger.debug("term_2 is not finite")
            if not np.isfinite(term_3):
                self.logger.debug("term_3 is not finite")
            if not np.isfinite(y_partial):
                self.logger.debug("y_partial is not finite")
            if not np.isfinite(s_f):
                self.logger.debug("s_f is not finite")
            raise RuntimeError("Non-finite value computed")

        return f


class HSolver(Solver):
    """DYNPOUND stage solver

    Parameters
    ----------
    sect : CrossSect
    bed_slope : float
    slope_ratio : float
    time_step : float
    c_comp : {'dkda', 'const k', 'k', 'dqda'}, optional
        Kinematic wave celerity computation method. The default is 'dkda'.

    Notes
    -----
    **Celerity computation methods.**

    *dkda*

    Use the derivative of conveyance with respect to area.

    .. math:: c = S_0^{1/2}\\frac{\\text{d}K}{\\text{d}A}

    where :math:`K` is conveyance.

    *const k*

    Use a constant :math:`K` value in the computation
    of celerity from [1]_ where

    .. math:: c = K\\frac{Q}{A}

    and :math:`K=1.7`.

    *k*

    Compute :math:`K` at each time step, where

    .. math:: c = K\\frac{Q}{A}

    and

    .. math::
        K = \\frac{5}{3} - \\frac{2A}{3B^2}\\frac{\\text{d}B}{\\text{d}A}.

    *dqda*

    Use the derivative of discharge with respect to area.

    .. math:: c = \\frac{\\text{d}Q}{\\text{d}A}

    """

    def h_solve(self, q, q_prime, h_prime, h0=None):

        # convergence tolerance
        tol = 0.1

        if h0 is None:
            h0 = h_prime

        root, r = newton(lambda h: self.zero_func(
            h, h_prime, q, q_prime), h0, tol=tol, full_output=True, disp=False)

        if not r.converged:
            self.logger.error("dynpound solver failed to converge after "
                              + "{} iterations".format(r.iterations))
            raise RuntimeError("dynpound zero function failed to converge")
        else:
            self.logger.debug("Converged to value " +
                              "{} after {} iterations".format(root,
                                                              r.iterations))

        return root


class QSolver(Solver):
    """DYNPOUND discharge solver

    Parameters
    ----------
    sect : CrossSect
    bed_slope : float
    slope_ratio : float
    time_step : float
    c_comp : {'dkda', 'const k', 'k', 'dqda'}, optional
        Kinematic wave celerity computation method. The default is 'dkda'.

    Notes
    -----
    **Celerity computation methods.**

    *dkda*

    Use the derivative of conveyance with respect to area.

    .. math:: c = S_0^{1/2}\\frac{\\text{d}K}{\\text{d}A}

    where :math:`K` is conveyance.

    *const k*

    Use a constant :math:`K` value in the computation
    of celerity from [1]_ where

    .. math:: c = K\\frac{Q}{A}

    and :math:`K=1.7`.

    *k*

    Compute :math:`K` at each time step, where

    .. math:: c = K\\frac{Q}{A}

    and

    .. math::
        K = \\frac{5}{3} - \\frac{2A}{3B^2}\\frac{\\text{d}B}{\\text{d}A}.

    *dqda*

    Use the derivative of discharge with respect to area.

    .. math:: c = \\frac{\\text{d}Q}{\\text{d}A}

    """

    def q_solve(self, h, h_prime, q_prime, q0=None):

        # convergence tolerance
        tol = 1  # cfs

        if q0 is None:
            q0 = q_prime

        root, r = newton(lambda q: self.zero_func(
            h, h_prime, q, q_prime), q0, tol=tol, full_output=True, disp=False)

        if not r.converged:
            self.logger.error("dynpound solver failed to converge after "
                              + "{} iterations".format(r.iterations))
            raise RuntimeError("dynpound zero function failed to converge")
        else:
            self.logger.debug("Converged to value " +
                              "{} after {} iterations".format(root,
                                                              r.iterations))

        return root
