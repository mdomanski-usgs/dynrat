import matplotlib.dates as mdates
import numpy as np
import pandas as pd

from dynrat.plot import time_series_axes


class TimeSeries:
    """Time series class

    Parameters
    ----------
    data : pandas.Series

    """

    def __init__(self, data):

        self._data = data.copy(deep=True)

    @staticmethod
    def _read_aq_csv(csv_path):

        df = pd.read_csv(csv_path, index_col=0, parse_dates=True)

        ts = df['Value']
        ts.index.name = 'DateTime'

        return ts

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

        ts = cls._read_aq_csv(csv_path)

        return cls(ts)

    def values(self):
        """Returns an array of observed values in this time
        series

        Returns
        -------
        numpy.ndarray

        """

        return self._data.values


class ObservedDischargeTimeSeries(TimeSeries):

    def plot(self, ax=None):

        ax = time_series_axes(ax)

        datetime = mdates.date2num(self._data.index.to_pydatetime())

        ax.scatter(datetime, self._data.values, color='darkorchid')

        return ax


class ContinuousTimeSeries(TimeSeries):

    def __init__(self, data, freq=None):

        if freq is None and data.index.freq is None:
            raise ValueError(
                "Continuous time series frequency must be specified")

        if freq is not None and data.index.freq is None and \
                data.index.freq != pd.tseries.offsets.DateOffset(seconds=freq):
            data = self._set_freq(data, freq, True)
        else:
            data = data.copy()

        super().__init__(data)

    @staticmethod
    def _set_freq(data, freq, interp_missing=False):

        freq = '{}S'.format(freq)
        index = pd.date_range(
            start=data.index[0], end=data.index[-1], freq=freq,
            tz=data.index.tz)
        index.name = 'DateTime'

        new_data = data[index]

        if interp_missing:
            new_data = new_data.interpolate()

        return new_data

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

        data = self._set_freq(self._data, freq, interp_missing)

        return self.__class__(data)

    def freq(self):
        """Returns the frequency of the observations of
        this data set

        Returns
        -------
        float

        """
        return self._data.index.freq.nanos/1e9

    @classmethod
    def from_aq_csv(cls, csv_path, freq=None):
        """Read time series from Aquarius CSV file

        Parameters
        ----------
        csv_path : str
            Path to Aquarius CSV file
        freq : float, optional


        """

        ts = cls._read_aq_csv(csv_path)

        if freq is None:
            index_diff = ts.index[1] - ts.index[0]
            freq = float(index_diff/np.timedelta64(1, 's'))

        return cls(ts, freq)


class RatedDischargeTimeSeries(ContinuousTimeSeries):

    def plot(self, ax=None):

        ax = time_series_axes(ax)

        datetime = mdates.date2num(self._data.index.to_pydatetime())

        ax.plot(datetime, self._data.values,
                label='Rated Discharge', linestyle='solid',
                color='darkslategray')
        ax.set_xlabel('Time')
        ax.set_ylabel('Discharge, in cfs')

        ax.legend()

        return ax


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
