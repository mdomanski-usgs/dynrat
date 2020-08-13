import matplotlib.dates as mdates
import matplotlib.pyplot as plt
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

    @staticmethod
    def _read_aq_csv(csv_path):

        df = pd.read_csv(csv_path, index_col=0, parse_dates=True)

        ts = df['Value']
        ts.index.name = 'DateTime'

        return ts

    @staticmethod
    def _time_series_axes(ax=None):

        if ax is None:
            ax = plt.axes()

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))

        return ax

    def data(self):
        """Returns a copy of the data contained in this
        time series

        Returns
        -------
        pandas.Series

        """

        return self._data.copy()

    def fill(self, other):
        """Fills values from other time series

        Fills na values in this time series with values
        from `other`.

        Parameters
        ----------
        other : TimeSeries

        """

        na_observations = self._data.isna()
        na_idx = self._data.index[na_observations]

        fill_idx = other._data.index.isin(na_idx)

        self._data[fill_idx] = other._data[fill_idx]

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

        ax = self._time_series_axes(ax)

        datetime = mdates.date2num(self._data.index.to_pydatetime())

        ax.scatter(datetime, self._data.values,
                   label='Observed Discrete Discharge', color='darkorchid')
        ax.legend()

        return ax


class ObservedStageTimeSeries(TimeSeries):

    def plot(self, ax=None):

        ax = self._time_series_axes(ax)

        datetime = mdates.date2num(self._data.index.to_pydatetime())

        ax.scatter(datetime, self._data.values,
                   label='Observed Discrete Stage', color='darkorchid')
        ax.legend()

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

        ax = self._time_series_axes(ax)

        datetime = mdates.date2num(self._data.index.to_pydatetime())

        ax.plot(datetime, self._data.values,
                label='WSC Computed Discharge', linestyle='solid',
                color='darkslategray')
        ax.set_xlabel('Time')
        ax.set_ylabel('Discharge, in cfs')

        ax.legend()

        return ax


class MeasuredStageTimeSeries(ContinuousTimeSeries):

    def plot(self, ax=None):

        ax = self._time_series_axes(ax)

        datetime = mdates.date2num(self._data.index.to_pydatetime())

        ax.plot(datetime, self._data.values, label='Measured Stage',
                linestyle='solid', color='darkslategray')
        ax.set_xlabel('Time')
        ax.set_ylabel('Stage, in ft')

        ax.legend()

        return ax


class ComputedDischargeTimeSeries(ContinuousTimeSeries):

    def plot(self, ax=None):

        ax = self._time_series_axes(ax)

        datetime = mdates.date2num(self._data.index.to_pydatetime())

        ax.plot(datetime, self._data.values, label='DYNRAT Computed Discharge',
                linestyle='solid', color='dodgerblue')
        ax.set_xlabel('Time')
        ax.set_ylabel('Discharge, in csf')

        ax.legend()

        return ax


def read_nwis_rdb(rdb_path):
    """Reads an NWIS RDB file containing field measurement
    data

    Parameters
    ----------
    rdb_path : str
        Path to RDB file

    Returns
    -------
    ObservedStageTimeSeries, ObservedDischargeTimeSeries
        Stage, discharge time series

    """

    time_zones = {'EST': 'EST5EDT',
                  'EDT': 'EST5EDT',
                  'CST': 'CST6CDT',
                  'CDT': 'CST6CDT',
                  'MST': 'MST7MDT',
                  'MDT': 'MST7MDT',
                  'PST': 'PST7PDT',
                  'PDT': 'PST7PDT'}

    with open(rdb_path) as f:
        lines = f.readlines()

    i = 0
    while lines[i][0] == '#':
        i += 1

    header_line = i
    header = lines[i].strip().split('\t')

    dt_column = header.index('measurement_dt')  # date and time
    tz_column = header.index('tz_cd')  # time zone
    h_column = header.index('gage_height_va')  # stage
    q_column = header.index('discharge_va')  # discharge

    dt_data = []
    h_data = []
    q_data = []

    for line in lines[header_line+2:]:

        line_data = line.strip().split('\t')

        try:
            datetime = pd.to_datetime(line_data[dt_column])
            stage = float(line_data[h_column])
            discharge = float(line_data[q_column])
        except IndexError:
            continue

        tz = line_data[tz_column]
        datetime = datetime.tz_localize(time_zones[tz])
        datetime = datetime.tz_convert('UTC')

        h_data.append(stage)
        q_data.append(discharge)
        dt_data.append(datetime)

    index = pd.DatetimeIndex(dt_data)

    stage_series = ObservedStageTimeSeries(pd.Series(index=index, data=h_data))
    discharge_series = ObservedDischargeTimeSeries(
        pd.Series(index=index, data=q_data))

    return stage_series, discharge_series


def read_nwis_csv(csv_path):
    """Reads a CSV file containing NWIS data

    This function reads CSV files obtained using the
    dataRetrieval R package.

    Parameters
    ----------
    csv_path : str
        Path to NWIS CSV file

    """

    with open(csv_path) as f:
        lines = f.readlines()

    header = lines[0].strip().split(',')

    dt_column = header.index('Date_Time')
    tz_column = header.index('tz_cd')
    q_column = header.index('Discharge')
    h_column = header.index('Gage_Height')

    dt_data = []
    h_data = []
    q_data = []

    for line in lines[1:]:

        line_data = line.strip().split(',')

        datetime = pd.to_datetime(line_data[dt_column])
        tz = line_data[tz_column]
        datetime = datetime.tz_localize(tz)
        datetime = datetime.tz_convert('UTC')
        dt_data.append(datetime)

        stage = float(line_data[h_column])
        h_data.append(stage)

        discharge = float(line_data[q_column])
        q_data.append(discharge)

    index = pd.DatetimeIndex(dt_data)

    stage_series = ObservedStageTimeSeries(pd.Series(index=index, data=h_data))
    discharge_series = ObservedDischargeTimeSeries(
        pd.Series(index=index, data=q_data))

    return stage_series, discharge_series


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
