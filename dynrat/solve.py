import numpy as np
import pandas as pd

import dynrat
from dynrat.timeseries import ComputedDischargeTimeSeries, ComputedStageTimeSeries


# module-level logger
logger = dynrat.logger.getChild(__name__)


class HTimeSeries:

    def __init__(self, solver):

        self._solver = solver
        self.logger = logger.getChild(self.__class__.__name__)

    def solve_ts(self, discharge_time_series, h0):
        """Solve stage from discharge time series

        Parameters
        ----------
        discharge_time_series : TimeSeries
            Discharge time series
        h0 : float
            Starting value of stage

        Returns
        -------
        ComputedDischargeTimeSeries

        """

        discharge_series = discharge_time_series.data()

        q = discharge_series.values[1:]
        q0 = discharge_series.values[0]

        h = np.nan * np.empty_like(q)

        try:
            h[0] = self._solver.h_solve(q[0], q0, h0)
        except RuntimeError:
            h[0] = np.nan
            self.logger.error("NaN encountered at index " +
                              "{}, timestamp {}".format(1,
                                                        discharge_series.index[1]))

            h_series = pd.Series(index=discharge_series.index[1:], data=h)

            return ComputedStageTimeSeries(h_series)

        for i in range(1, len(q)):

            try:
                h[i] = self._solver.h_solve(q[i], q[i - 1], h[i - 1])
            except RuntimeError:
                h[i] = np.nan

            dt_step = discharge_series.index[i+1]

            if np.isnan(h[i]):
                self.logger.error("NaN encountered at index " +
                                  "{}, timestamp {}".format(i+1, dt_step))
                break
            if np.iscomplex(h[i]):
                self.logger.error("Complex value encountered at index " +
                                  "{}, timestamp {}".format(i+1, dt_step))
                break
            else:
                self.logger.debug(
                    "Computed {} for timestamp {}".format(h[i], dt_step))

        h_series = pd.Series(index=discharge_series.index[1:], data=h)

        return ComputedStageTimeSeries(h_series)


class QTimeSeries:

    def __init__(self, solver):

        self._solver = solver
        self.logger = logger.getChild(self.__class__.__name__)

    def solve_ts(self, stage_time_series, q0):
        """Solve discharge from stage time series

        Parameters
        ----------
        stage_time_series : MeasuredStageTimeSeries
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

        try:
            q[0] = self._solver.q_solve(h[0], h0, q0)
        except RuntimeError:
            q[0] = np.nan
            self.logger.error("NaN encountered at index " +
                              "{}, timestamp {}".format(1,
                                                        stage_series.index[1]))

            q_series = pd.Series(index=stage_series.index[1:], data=q)

            return ComputedDischargeTimeSeries(q_series)

        for i in range(1, len(h)):

            try:
                q[i] = self._solver.q_solve(h[i], h[i - 1], q[i - 1])
            except RuntimeError:
                q[i] = np.nan

            dt_step = stage_series.index[i+1]

            if np.isnan(q[i]):
                self.logger.error("NaN encountered at index " +
                                  "{}, timestamp {}".format(i+1, dt_step))
                break
            if np.iscomplex(q[i]):
                self.logger.error("Complex value encountered at index " +
                                  "{}, timestamp {}".format(i+1, dt_step))
                break
            else:
                self.logger.debug(
                    "Computed {} for timestamp {}".format(q[i], dt_step))

        q_series = pd.Series(index=stage_series.index[1:], data=q)

        return ComputedDischargeTimeSeries(q_series)
