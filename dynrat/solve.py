import logging

import numpy as np
import pandas as pd

from dynrat import ch
from dynrat.timeseries import ComputedDischargeTimeSeries


class QTimeSeries:

    def __init__(self, solver):

        self._solver = solver
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.CRITICAL)
        self.logger.addHandler(ch)

    def solve_ts(self, stage_time_series, q0):
        """Solve discharge from stage time series

        Parameters
        ----------
        MeasuredStageTimeSeries
            Stage time series
        q0 : float
            Starting value of discharge

        Returns
        -------
        ComputedDischargeTimeSeries

        """

        stage_series = stage_time_series.data()

        h = stage_series.values[1:]
        h0 = stage_series.values[0]

        q = np.nan * np.empty_like(h)

        q[0] = self._solver.q_solve(h[0], h0, q0)

        for i in range(1, len(h)):
            q[i] = self._solver.q_solve(h[i], h[i - 1], q[i - 1])
            if np.isnan(q[i]):
                dt_step = stage_series.index[i]
                self.logger.error("NaN encountered at index " +
                                  " {}, index {}".format(i, dt_step))
                break

        q_series = pd.Series(index=stage_series.index[1:], data=q)

        return ComputedDischargeTimeSeries(q_series)
