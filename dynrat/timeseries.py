import numpy as np


class QTimeSeries:

    def __init__(self, solver):

        self._solver = solver

    def solve_ts(self, h_time_series, q0, h0):
        """Solve discharge from stage time series

        Parameters
        ----------
        h_time_series : array_like
            Stage time series
        q0 : float
            Starting value of discharge
        h0 : float
            Starting value of stage

        Returns
        -------
        ndarray
            Discharge time series

        """

        h = np.array(h_time_series)

        q = np.nan * np.empty_like(h)

        q[0] = self._solver.q_solve(h[0], h0, q0)

        for i in range(1, len(h)):
            try:
                q[i] = self._solver.q_solve(h[i], h[i - 1], q[i - 1])
            except RuntimeError:
                break

        return q
