import copy

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

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%y %H:%M'))
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

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

    def subset_dt(self, start=None, end=None):
        """Return a subset of this time series based on
        datetime values

        Parameters
        ----------
        start : str or pandas.Timestamp, optional
        end : str or pandas.Timestamp, optional

        Returns
        -------
        TimeSeries
            Subset of this time series

        """

        subset_tf = np.full_like(self._data.index, True, bool)

        if start is not None:
            start_dt = pd.to_datetime(start)
            if start_dt.tz is None:
                start_dt = start_dt.tz_localize(self._data.index.tz)
            after_start_tf = self._data.index >= start_dt
            subset_tf = subset_tf & after_start_tf

        if end is not None:
            end_dt = pd.to_datetime(end)
            if end_dt.tz is None:
                end_dt = end_dt.tz_localize(self._data.index.tz)
            before_end_tf = self._data.index <= end_dt
            subset_tf = subset_tf & before_end_tf

        return self.__class__(self._data[subset_tf])

    def to_csv(self, csv_path):
        """Writes the data contained in this time series to
        a CSV file

        Parameters
        ----------
        csv_path : str
            Path to CSV file

        """

        self._data.to_csv(csv_path, index_label='DateTime')

    def values(self):
        """Returns an array of observed values in this time
        series

        Returns
        -------
        numpy.ndarray

        """

        return self._data.values


class ObservedDischargeTimeSeries(TimeSeries):

    def __init__(self, data, meas_no=None):

        self._meas_no = meas_no

        super().__init__(data)

    def meas_number(self):

        return copy.copy(self._meas_no)

    def plot(self, ax=None):

        ax = self._time_series_axes(ax)

        datetime = mdates.date2num(self._data.index.to_pydatetime())

        ax.scatter(datetime, self._data.values,
                   label='Observed Discrete Discharge', color='darkorchid')
        ax.legend()

        return ax

    def subset_dt(self, start=None, end=None):

        subset = super().subset_dt(start, end)

        subset_dt = self._data.index.isin(subset._data.index)

        self_meas_no = np.asarray(self._meas_no)
        subset_meas_no = self_meas_no[subset_dt]

        subset._meas_no = list(subset_meas_no)

        return subset


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
        prop : {'top width', 'area', 'wetted perimeter'}
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
        elif prop == 'wetted perimeter':
            xs_method = xs.wetted_perimeter
            label = 'Wetted perimeter'
        else:
            raise ValueError("Unrecognized property: {}".format(prop))

        xs_values = np.empty_like(self._data.values)

        try:
            xs_values = xs_method(self._data.values)
        except ValueError as e:

            # handle case when xs_method can't handle an array argument
            if 'Use a.any() or a.all()' in e.args[0]:
                for i, v in enumerate(self._data.values):
                    xs_values[i] = xs_method(v)
            else:
                raise e

        ax = self._time_series_axes(ax)

        datetime = mdates.date2num(self._data.index.to_pydatetime())

        ax.plot(datetime, xs_values, label=label)
        ax.legend()

        return ax

    def plot(self, ax=None):

        ax = self._time_series_axes(ax)

        datetime = mdates.date2num(self._data.index.to_pydatetime())

        ax.plot(datetime, self._data.values, label='Measured Stage',
                linestyle='solid', color='darkslategray')
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
        ax.set_ylabel('Relative Error, in %')

        ax.legend()

        return ax

    def relative_error(self, rated_discharge):
        """Computes relative error

        Parameters
        ----------
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


def parse_nwis_csv(csv_path):
    """Parse a CSV file containing continuous NWIS data.

    Parses a CSV obtained using the dataRetrieval R package and
    returns a Pandas DataFrame

    Parameters
    ----------
    csv_path : str
        Path to CSV file

    Returns
    -------
    pandas.DataFrame
        NWIS stage and discharge time series

    """

    with open(csv_path) as f:
        lines = f.readlines()

    header = lines[0].strip().replace('"', '').split(',')

    dt_column = header.index('dateTime')
    tz_column = header.index('tz_cd')
    q_column = header.index('X_00060_00000')
    h_column = header.index('X_00065_00000')

    dt_data = []
    h_data = []
    q_data = []

    for line in lines[1:]:

        line_data = line.strip().split(',')

        line_data = [col.replace('"', '') for col in line_data]

        datetime = pd.to_datetime(line_data[dt_column])
        tz = line_data[tz_column].strip('"')
        datetime = datetime.tz_localize(tz)
        datetime = datetime.tz_convert('UTC')
        dt_data.append(datetime)

        try:
            stage = float(line_data[h_column])
        except ValueError:
            stage = np.nan
        h_data.append(stage)

        try:
            discharge = float(line_data[q_column])
        except ValueError:
            discharge = np.nan
        q_data.append(discharge)

    index = pd.DatetimeIndex(dt_data)
    index.name = 'DateTime'

    data = np.stack([h_data, q_data], axis=1)
    columns = ['Stage', 'Discharge']

    return pd.DataFrame(data=data, index=index, columns=columns)


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
                  'PDT': 'PST7PDT',
                  '': 'UTC'}

    with open(rdb_path) as f:
        lines = f.readlines()

    i = 0
    while lines[i][0] == '#':
        i += 1

    header_line = i
    header = lines[i].strip().split('\t')

    dt_column = header.index('measurement_dt')  # date and time
    meas_num_column = header.index('measurement_nu')  # measurement number
    tz_column = header.index('tz_cd')  # time zone
    h_column = header.index('gage_height_va')  # stage
    q_column = header.index('discharge_va')  # discharge

    dt_data = []
    meas_num_data = []
    h_data = []
    q_data = []

    for line in lines[header_line+2:]:

        line_data = line.strip().split('\t')

        try:
            datetime = pd.to_datetime(line_data[dt_column])
        except IndexError:
            continue

        try:
            stage = float(line_data[h_column])
        except (IndexError, ValueError):
            stage = np.nan

        try:
            discharge = float(line_data[q_column])
        except (IndexError, ValueError):
            discharge = np.nan

        tz = line_data[tz_column]
        datetime = datetime.tz_localize(time_zones[tz])
        datetime = datetime.tz_convert('UTC')

        meas_num = line_data[meas_num_column]

        h_data.append(stage)
        q_data.append(discharge)
        dt_data.append(datetime)
        meas_num_data.append(meas_num)

    index = pd.DatetimeIndex(dt_data)

    stage_series = ObservedStageTimeSeries(pd.Series(index=index, data=h_data))
    discharge_series = ObservedDischargeTimeSeries(
        pd.Series(index=index, data=q_data), meas_no=meas_num_data)

    return stage_series, discharge_series


def read_nwis_hdf(hdf_path, freq=None, interp_missing=False):
    """Reads an HDF file containing continuous NWIS data

    Reads an HDF file saved from a Pandas DataFrame created with
    :py:func:`parse_nwis_csv`.

    Parameters
    ----------
    hdf_path : str
        Path to HDF file
    freq : float, optional
    interp_missing : boolean, optional

    Returns
    -------
    MeasuredStageTimeSeries, RatedDischargeTimeSeries
        Stage, discharge time series

    """

    nwis_df = pd.read_hdf(hdf_path, 'nwis')
    index = nwis_df.index
    h_data = nwis_df['Stage'].values
    q_data = nwis_df['Discharge'].values

    if freq is None:
        index_diff = index[1] - index[0]
        freq = float(index_diff/np.timedelta64(1, 's'))

    stage_series = MeasuredStageTimeSeries(
        pd.Series(index=index, data=h_data), freq, interp_missing)
    discharge_series = RatedDischargeTimeSeries(
        pd.Series(index=index, data=q_data), freq, interp_missing)

    return stage_series, discharge_series
