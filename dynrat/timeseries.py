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
        from `other`. Returns a new time series object.

        Parameters
        ----------
        other : TimeSeries

        Returns
        -------
        TimeSeries

        """

        na_observations = self._data.isna()
        na_idx = self._data.index[na_observations]

        isin_other = other._data.index.isin(na_idx)
        isin_idx = other._data.index[isin_other]

        fill_idx = na_idx.intersection(isin_idx)

        data = self._data.copy()

        data[fill_idx] = other._data[fill_idx]

        return self.__class__(data)

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

    def null_obs(self):
        """Returns the number of null observations in this
        time series

        Returns
        -------
        int
            Number of null observations

        """

        return self._data.isna().sum()

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
    """Time series of continuously observed parameter

    Parameters
    ----------
    data : pandas.Series
        Time series data
    freq : float or None, optional
        Observation frequency. The default is None. If
        None, the frequency must be specified in the series
        DatetimeIndex.
    interp_missing : boolean, optional
        Interpolatel missing observations. The default is
        False.

    """

    def __init__(self, data, freq=None, interp_missing=False):

        if freq is None and data.index.freq is None:
            raise ValueError(
                "Continuous time series frequency must be specified")

        if freq is not None and data.index.freq is None and \
                data.index.freq != pd.tseries.offsets.DateOffset(seconds=freq):
            data = self._set_freq(data, freq, interp_missing)
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
    def from_aq_csv(cls, csv_path, freq=None, interp_missing=False):
        """Read time series from Aquarius CSV file

        Parameters
        ----------
        csv_path : str
            Path to Aquarius CSV file
        freq : float, optional
            Observation frequency, in seconds
        interp_missing : boolean
            Interpolate missing observations

        Returns
        -------
        ContinuousTimeSeries

        """

        ts = cls._read_aq_csv(csv_path)

        if freq is None:
            index_diff = ts.index[1] - ts.index[0]
            freq = float(index_diff/np.timedelta64(1, 's'))

        return cls(ts, freq, interp_missing)


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

    def cross_section_plot(self, xs, prop, ax=None):
        """Plot time series of cross section property

        Parameters
        ----------
        xs : Sect
            Cross section for computing property
        prop : {'top width', 'area'}
            Cross section property to plot
        ax : matplotlib.axes.Axes, optional
            Axes to plot on

        Returns
        -------
        matplotlib.axes.Axes

        """

        if prop == 'top width':
            xs_method = xs.top_width
            label = 'Top width'
        elif prop == 'area':
            xs_method = xs.area
            label = 'Area'
        else:
            raise ValueError("Unrecognized property: {}".format(prop))

        xs_values = np.empty_like(self._data.values)
        for i, v in enumerate(self._data.values):
            try:
                xs_values[i] = xs_method(v)
            except ValueError:
                xs_values[i] = np.nan

        ax = self._time_series_axes(ax)

        datetime = mdates.date2num(self._data.index.to_pydatetime())

        ax.plot(datetime, xs_values, label=label)
        ax.set_xlabel('Time')
        ax.legend()

        return ax

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

    def mean_error(self, rated_discharge, relative=False):

        q_rated = rated_discharge.data()

        intersect_idx = self._data.index.intersection(q_rated.index)

        q_meas = q_rated[intersect_idx]
        q_comp = self._data[intersect_idx]

        error = q_comp - q_meas

        if relative:
            error = 100 * error / q_meas

        mean_error = np.mean(error)

        return mean_error

    def plot(self, ax=None):

        ax = self._time_series_axes(ax)

        datetime = mdates.date2num(self._data.index.to_pydatetime())

        ax.plot(datetime, self._data.values, label='DYNRAT Computed Discharge',
                linestyle='solid', color='dodgerblue')
        ax.set_xlabel('Time')
        ax.set_ylabel('Discharge, in csf')

        ax.legend()

        return ax

    def plot_relative_error(self, rated_discharge, ax=None):
        """Plots relative error time series

        Parameters
        ----------
        rated_discharge : RatedDischargeTimeSeries
        ax : matplotlib.axes.Axes

        Returns
        -------
        matplotlib.axes.Axes

        """

        ax = self._time_series_axes(ax)

        relative_error = self.relative_error(rated_discharge)

        datetime = mdates.date2num(relative_error.index)

        ax.plot(datetime, relative_error.values, label='Relative Error',
                linestyle='solid', color='darkorchid')
        ax.set_xlabel('Time')
        ax.set_ylabel('Relative Error, in %')

        ax.legend()

        return ax

    def relative_error(self, rated_discharge):
        """Computes relative error

        Paramters
        ---------
        rated_discharge : RatedDischargeTimeSeries

        Returns
        -------
        pandas.Series

        """

        q_rated = rated_discharge.data()

        intersect_idx = self._data.index.intersection(q_rated.index)

        q_meas = q_rated[intersect_idx]
        q_comp = self._data[intersect_idx]

        relative_error = 100*(q_comp - q_meas)/q_meas

        return pd.Series(index=intersect_idx, data=relative_error)

    def rmse(self, rated_discharge):

        q_rated = rated_discharge.data()

        intersect_idx = self._data.index.intersection(q_rated.index)

        q_meas = q_rated[intersect_idx]
        q_comp = self._data[intersect_idx]

        sq_error = (q_comp - q_meas)**2
        rmse = np.sqrt(np.mean(sq_error))

        return rmse


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
    """Reads a CSV file containing continuous NWIS data

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

    index_diff = index[1] - index[0]
    freq = float(index_diff/np.timedelta64(1, 's'))

    stage_series = MeasuredStageTimeSeries(
        pd.Series(index=index, data=h_data), freq)
    discharge_series = RatedDischargeTimeSeries(
        pd.Series(index=index, data=q_data), freq)

    return stage_series, discharge_series
