import numpy as np
from scipy.optimize import newton

import dynrat
from dynrat import GRAVITY


logger = dynrat.logger.getChild(__name__)


class QSolver:

    def __init__(self, sect, bed_slope, slope_ratio, time_step):

        self._bed_slope = bed_slope
        self._sect = sect
        self._slope_ratio = slope_ratio
        self._time_step = time_step

        self.logger = logger.getChild(self.__class__.__name__)

    def _celerity(self, h, h_prime, q, q_prime):

        area = self._sect.area(h)

        celerity = 1.5*q/area

        return celerity

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
        else:
            self.logger.debug("Converged to value " +
                              "{} after {} iterations".format(root,
                                                              r.iterations))

        return root

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
