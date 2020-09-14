import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator

from dynrat.timeseries import ContinuousTimeSeries, TimeSeries


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
