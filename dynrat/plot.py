import matplotlib.dates as mdates
import matplotlib.pyplot as plt


def time_series_axes(ax=None):

    if ax is None:
        ax = plt.axes()

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))

    return ax


def stage_discharge_plot(stage, discharge, ax=None):

    if ax is None:
        ax = plt.axes()

    ax.plot()
