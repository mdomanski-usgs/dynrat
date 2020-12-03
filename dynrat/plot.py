from matplotlib.collections import LineCollection
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
import numpy as np

from dynrat.timeseries import ContinuousTimeSeries, TimeSeries


def multicolor_h_vs_q(stage, discharge, ax=None, colormap='binary'):

    if ax is None:
        ax = plt.axes()

    h_series = stage.data()
    q_series = discharge.data()

    inter_idx = h_series.index.intersection(q_series.index)

    x = q_series[inter_idx].values
    y = h_series[inter_idx].values
    time_as_float = inter_idx.values.astype(float)
    norm_time_as_float = (time_as_float - time_as_float.min()) / \
        (time_as_float.max() - time_as_float.min())

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    norm = plt.Normalize(norm_time_as_float.min(), norm_time_as_float.max())
    lc = LineCollection(segments, cmap=colormap, norm=norm)

    lc.set_array(norm_time_as_float)

    lc.set_linewidth(2)
    ax.add_collection(lc)

    margin = 0.1

    ax.set_xlabel('Discharge, in cfs')
    x_range = x.max() - x.min()
    ax.set_xlim(x.min() - margin*x_range, x.max() + margin*x_range)

    ax.set_ylabel('Stage, in ft')
    y_range = y.max() - y.min()
    ax.set_ylim(y.min() - margin*y_range, y.max() + margin*y_range)

    return ax


def stage_discharge_plot(stage, discharge, ax=None, color=None, label=None):
    """Plot stage vs. discharge

    Parameters
    ----------
    stage : TimeSeries
        Stage time series
    discharge : TimeSeries
        Discharge time series
    ax : matplotlib.axes.Axes, optional
        If None, a new axes is created and returned.
    color : str, optional
        Color for the line. If None and stage and discharge
        are :class:`.ContinuousTimeSeries`,
        ``'darkslategray'`` is used. If None and stage and
        discharge are instances of a :class:`.TimeSeries`
        subclass, ``'darkorchid'`` is used.
    label : str, optional
        Label for the line. If None and stage and discharge
        are :class:`.ContinuousTimeSeries`, ``'WSC Computed
        Discharge'`` is used. If None and stage and
        discharge are instances of a :class:`.TimeSeries`
        subclass, ``'Observed Discrete Discharge'`` is used.

    Return
    ------
    matplotlib.axes.Axes

    """

    if ax is None:
        ax = plt.axes()

    if isinstance(stage, ContinuousTimeSeries) and \
            isinstance(discharge, ContinuousTimeSeries):

        if color is None:
            color = 'darkslategray'

        if label is None:
            label = 'WSC Computed Discharge'

        h_series = stage.data()
        q_series = discharge.data()

        inter_idx = h_series.index.intersection(q_series.index)

        ax.plot(q_series[inter_idx].values, h_series[inter_idx].values,
                label=label, linestyle='solid',
                color=color)

    elif isinstance(stage, TimeSeries) and isinstance(discharge, TimeSeries):

        if color is None:
            color = 'darkorchid'

        if label is None:
            label = 'Observed Discrete Discharge'

        ax.scatter(discharge.values(), stage.values(),
                   label=label, color=color)

    else:
        raise TypeError("Unrecognized types of time series")

    ax.set_xlabel('Discharge, in cfs')
    ax.set_ylabel('Stage, in ft')

    ax.legend()

    return ax
