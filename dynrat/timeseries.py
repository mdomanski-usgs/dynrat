import numpy as np
import pandas as pd


class TimeSeries:
    """Time series class

    Parameters
    ----------
    data : pandas.Series

    """

    def __init__(self, data):

        self._data = data.copy(deep=True)

    def data(self):
        """Returns a copy of the data contained in this
        time series

        Returns
        -------
        pandas.Series

        """

        return self._data.copy()

    @classmethod
    def from_aq_csv(cls, csv_path):
        """Reads time series from a CSV file obtained from
        Aquarius

        Parameters
        ----------
        csv_path : str
            Path to CSV file

        Returns
        -------
        TimeSeries

        """

        df = pd.read_csv(csv_path, index_col=0, parse_dates=True)

        ts = df['Value']
        ts.index.name = 'DateTime'

        return cls(ts)

    def values(self):
        """Returns an array of observed values in this time
        series

        Returns
        -------
        numpy.ndarray

        """

        return self._data.values


class ContinuousTimeSeries(TimeSeries):

    def change_freq(self, freq, interp_missing=False):
        """Change the frequency of this time series

        Parameters
        ----------
        time_step : float
            New time step, in seconds
        interp_missing : boolean, optional
            Interpolate missing values in the new time
            series

        Returns
        -------
        ContinuousTimeSeries

        """

        freq = pd.tseries.offsets.DateOffset(seconds=freq)
        index = pd.date_range(
            start=self._data.index[0], end=self._data.index[-1], freq=freq,
            tz=self._data.index.tz)
        index.name = 'DateTime'

        data = self._data[index]

        if interp_missing:
            data = data.interpolate()

        return self.__class__(data)


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
