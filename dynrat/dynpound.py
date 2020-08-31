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

    def _celerity(self, h, top_width):

        dh = 0.01
        dk = self._sect.conveyance(h + dh/2) - self._sect.conveyance(h - dh/2)
        celerity = self._bed_slope**(1/2)/top_width*(dk/dh)

        return celerity

    def q_solve(self, h, h_prime, q_prime, q0=None):

        # convergence tolerance
        tol = 1.0  # cfs

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

        beta = self._sect.vel_dist_factor(h)

        top_width = self._sect.top_width(h)

        celerity = self._celerity(h, top_width)

        dh = h - h_prime
        y_partial = -1/celerity*dh/self._time_step - \
            2/3*self._bed_slope/self._slope_ratio**2

        term_1 = 1/(GRAVITY*area)*(q - q_prime)/self._time_step
        term_2 = beta*(2*q)/(GRAVITY*area**2) * \
            (area - area_prime)/self._time_step
        term_3 = (1 - beta*top_width*q**2/(GRAVITY*area**3))*y_partial

        k = self._sect.conveyance(h)
        # k_prime = self._sect.conveyance(h_prime)

        # q = k*s_f*(1/2)
        # q_prime = k_prime*s_f_prime(1/2)

        s_f = (q/k)**2

        return term_1 - term_2 + term_3 + s_f - self._bed_slope
