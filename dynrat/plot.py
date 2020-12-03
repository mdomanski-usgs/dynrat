from matplotlib.collections import LineCollection
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
import numpy as np

from dynrat.timeseries import ContinuousTimeSeries, TimeSeries


def multicolor_h_vs_q(stage, discharge, axs=None, colormap='binary'):

    if axs is None:
        fig = plt.figure()
        ax1 = plt.subplot2grid((4, 1), (0, 0), colspan=1, rowspan=1, fig=fig)
        ax2 = plt.subplot2grid((4, 1), (1, 0), colspan=1, rowspan=3, fig=fig)

    h_series = stage.data()
    q_series = discharge.data()

    inter_idx = h_series.index.intersection(q_series.index)

    q_values = q_series[inter_idx].values
    h_values = h_series[inter_idx].values
    time_as_float = inter_idx.values.astype(float)
    time_range = time_as_float.max() - time_as_float.min()
    norm_time_as_float = (time_as_float - time_as_float.min()) / time_range
    norm = plt.Normalize(norm_time_as_float.min(), norm_time_as_float.max())

    # discharge vs time hydrograph
    q_t_points = np.array([norm_time_as_float, q_values]).T.reshape(-1, 1, 2)
    q_t_segments = np.concatenate([q_t_points[:-1], q_t_points[1:]], axis=1)
    q_t_lc = LineCollection(q_t_segments, cmap=colormap, norm=norm)
    q_t_lc.set_array(norm_time_as_float)
    q_t_lc.set_linewidth(2)
    ax1.add_collection(q_t_lc)

    # stage vs discharge plot
    h_q_points = np.array([q_values, h_values]).T.reshape(-1, 1, 2)
    h_q_segments = np.concatenate([h_q_points[:-1], h_q_points[1:]], axis=1)
    h_q_lc = LineCollection(h_q_segments, cmap=colormap, norm=norm)
    h_q_lc.set_array(norm_time_as_float)
    h_q_lc.set_linewidth(2)
    ax2.add_collection(h_q_lc)

    h_range = h_values.max() - h_values.min()
    q_range = q_values.max() - q_values.min()

    margin = 0.1

    q_lim = (q_values.min() - margin*q_range,
             q_values.max() + margin*q_range)

    h_lim = (h_values.min() - margin*h_range,
             h_values.max() + margin*h_range)

    ax1.set_ylabel('Discharge, in cfs')
    ax1.tick_params(axis='x', which='both', bottom=False,
                    top=False, labelbottom=False)
    ax1.set_ylim(q_lim)

    ax2.set_xlabel('Discharge, in cfs')
    ax2.set_xlim(q_lim)
    ax2.set_ylabel('Stage, in ft')
    ax2.set_ylim(h_lim)

    return fig


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
