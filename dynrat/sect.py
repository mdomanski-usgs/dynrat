from abc import abstractmethod

import matplotlib.pyplot as plt
import numpy as np

from anchovy.crosssection import CrossSection as AnchovyXS

from dynrat.frict import TableFrict


class Sect:
    """Interface for cross section properties

    """

    @abstractmethod
    def area(self, *args):
        """Returns cross section area"""

        pass

    @abstractmethod
    def top_with(self, *args):
        """Returns cross section top width"""

        pass


class TableSect(Sect):
    """Cross section properties from a table of computed
    stage/property values

    The cross section property methods of this class
    linearly interpolate cross section properties with
    stage. `stage`, `area`, and `top_width` must be one-
    dimensional and have two or more elements. `stage` must
    be sorted in ascending order.

    Parameters
    ----------
    stage : array_like
        Stage
    area : array_like
        Cross section area
    top_width : array_like
        Cross section top width

    """

    def __init__(self, stage, area, top_width):

        self._stage = np.array(stage)
        self._area = np.array(area)
        self._top_width = np.array(top_width)

        if self._stage.ndim != 1:
            raise ValueError("stage must be one-dimensional")

        if self._stage.size < 2:
            raise ValueError("stage must at least have two elements")

        if not np.alltrue(np.diff(stage) >= 0):
            raise ValueError("stage must be sorted in ascending order")

        if self._area.ndim != 1:
            raise ValueError("area must be one-dimensional")

        if self._area.size < 2:
            raise ValueError("area must at least have two elements")

        if self._top_width.ndim != 1:
            raise ValueError("top_width must be one-dimensional")

        if self._top_width.size < 2:
            raise ValueError("top_width must at least have two elements")

        n_stage = self._stage.size

        if n_stage != self._area.size or n_stage != self._top_width.size:
            raise ValueError(
                "stage, area, and top_width must have the same size")

    def area(self, stage, *args):
        """Returns cross section area

        Parameters
        ----------
        stage : array_like
            Stage

        Returns
        -------
        numpy.ndarray

        """

        return np.interp(stage, self._stage, self._area)

    def top_width(self, stage, *args):
        """Returns cross section top width

        Parameters
        ----------
        stage : array_like
            Stage

        Returns
        -------
        numpy.ndarray

        """

        return np.interp(stage, self._stage, self._top_width)


class CrossSect(Sect):
    """Cross section

    Parameters
    ----------
    xs : anchovy.crosssection.CrossSection
        Instance of a cross section from the anchovy package

    """

    def __init__(self, xs):

        self._xs = xs

        self._station, self._elevation = xs.coordinates()

        self._e_min = self._elevation.min()
        self._e_max = self._elevation.max()

        e = np.linspace(self._e_min, self._e_max)

        area = xs.area(e)
        top_width = xs.top_width(e)
        roughness = xs.roughness(e)

        self._sect = TableSect(e, area, top_width)
        self._frict = TableFrict(e, roughness)

    def area(self, stage):
        """Computes area of this cross section

        Parameters
        ----------
        stage : float

        Returns
        -------
        float

        """

        if stage < self._e_min or self._e_max < stage:
            raise ValueError(
                "Stage is outside of the range of this cross section")

        return self._sect.area(stage)

    @classmethod
    def from_csv(cls, csv_path):

        station, elevation = np.loadtxt(
            csv_path, delimiter=',', skiprows=1, unpack=True)

        # roughness isn't used here
        xs = AnchovyXS(station, elevation, 0.035)

        return cls(xs)

    def plot(self, ax=None):
        """Plots the coordinates of this cross section

        Parameters
        ----------
        ax : matplotlib.axes.Axes

        Returns
        -------
        matplotlib.axes.Axes

        """

        ax = self._xs.plot(ax=ax)

        ax.set_ylabel('Stage, in feet')

        return ax

    def top_width(self, stage):
        """Computes the top width for this cross section at a given stage

        Parameters
        ----------
        stage : float

        Returns
        -------
        float

        """

        if stage < self._e_min or self._e_max < stage:
            raise ValueError(
                "Stage is outside of the range of this cross section")

        return self._sect.top_width(stage)
