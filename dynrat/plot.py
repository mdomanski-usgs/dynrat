import matplotlib.pyplot as plt

from dynrat.timeseries import ContinuousTimeSeries, TimeSeries


def stage_discharge_plot(stage, discharge, ax=None):

    if ax is None:
        ax = plt.axes()

    if isinstance(stage, ContinuousTimeSeries) and \
            isinstance(discharge, ContinuousTimeSeries):

        h_series = stage.data()
        q_series = discharge.data()

        union_idx = h_series.index.union(q_series.index)

        ax.plot(q_series[union_idx], h_series[union_idx],
                label='WSC Computed Discharge', linestyle='solid',
                color='darkslategray')

    elif isinstance(stage, TimeSeries) and isinstance(discharge, TimeSeries):

        ax.scatter(discharge.values(), stage.values(),
                   label='Observed Discrete Discharge', color='darkorchid')

    else:
        raise TypeError("Unrecognized types of time series")

    ax.set_xlabel('Discharge, in cfs')
    ax.set_ylabel('Stage, in ft')

    ax.legend()

    return ax
