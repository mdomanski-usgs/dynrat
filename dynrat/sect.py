from abc import abstractmethod

import matplotlib.pyplot as plt
import numpy as np

from anchovy.crosssection import CrossSection as AnchovyXS

import dynrat
from dynrat.frict import TableFrict

logger = dynrat.logger.getChild(__name__)


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

    @abstractmethod
    def wetted_perimeter(self, *args):
        """Returns """


class TableSect(Sect):
    """Cross section properties from a table of computed
    stage/property values

    The cross section property methods of this class
    linearly interpolate cross section properties with
    stage. The property arrays are defined in kwargs.
    ``'stage'`` must be defined in kwargs.

    Parameters
    ----------
    kwargs : dict

    """

    def __init__(self, **kwargs):

        self._methods = []

        self.logger = logger.getChild(self.__class__.__name__)

        stage = kwargs.pop('stage', None)

        if stage is None:
            raise RuntimeError("stage must be passed as a kwarg")

        self._stage = np.array(stage)

        if self._stage.ndim != 1:
            raise ValueError("stage must be one-dimensional")

        if self._stage.size < 2:
            raise ValueError("stage must at least have two elements")

        if not np.alltrue(np.diff(stage) >= 0):
            raise ValueError("stage must be sorted in ascending order")

        for k, v in kwargs.items():
            v_array = np.array(v)

            if v_array.ndim != 1:
                raise ValueError("{} must be one-dimensional".format(k))

            if v_array.size < 2:
                raise ValueError("{} must have at least two elements")

            self.logger.debug("Adding {}".format('_' + k))

            setattr(self, '_' + k, v_array)
            self._methods.append(k)

    def __getattribute__(self, name):

        methods = super().__getattribute__('_methods')

        if name in methods:

            return lambda stage: self._interp(name, stage)

        else:

            return super().__getattribute__(name)

    def _interp(self, name, stage):

        attr = getattr(self, '_' + name)

        self.logger.debug(
            "Interpolating {} at stage {}".format('_' + name, stage))

        return np.interp(stage, self._stage, attr)

    def to_csv(self, csv_path):
        """Write this table to a CSV file

        Parameters
        ----------
        csv_path : str
            Path to write CSV file to

        """

        data = [self._stage]
        columns = ['stage']

        for name in self._methods:
            columns.append(name)
            data.append(getattr(self, '_' + name))

        X = np.stack(data, axis=1)

        header = ','.join(columns)

        np.savetxt(csv_path, X, delimiter=',', header=header)


class CrossSect(Sect):
    """Cross section

    Parameters
    ----------
    xs : anchovy.crosssection.CrossSection
        Instance of a cross section from the anchovy package

    """

    def __init__(self, xs):

        self.logger = logger.getChild(self.__class__.__name__)
        self.logger.debug("Initializing {}".format(self.__class__.__name__))

        self._xs = xs

        self._station, self._elevation = xs.coordinates()

        dh = 0.1

        self._e_min = self._elevation.min()
        self._e_max = self._elevation.max()
        num = int(np.ceil((self._e_max - self._e_min)/dh))

        e = np.linspace(self._e_min, self._e_max, num)

        kwargs = {'stage': e,
                  'area': xs.area(e),
                  'conveyance': xs.conveyance(e),
                  'top_width': xs.top_width(e),
                  'vel_dist_factor': xs.vel_dist_factor(e),
                  'wetted_perimeter': xs.wetted_perimeter(e)}

        self._sect = TableSect(**kwargs)

    def area(self, stage):
        """Computes area of this cross section

        Parameters
        ----------
        stage : float

        Returns
        -------
        float

        """

        if not np.isfinite(stage):
            self.logger.warning("Non-finite stage passed to area method")

        if stage < self._e_min or self._e_max < stage:
            self.logger.warning(
                "Stage {} is outside of ".format(stage) +
                "the range of this cross section")
            return self._xs.area(stage)

        return self._sect.area(stage)

    def conveyance(self, stage):

        if not np.isfinite(stage):
            self.logger.warning("Non-finite stage passed to conveyance method")

        if stage < self._e_min or self._e_max < stage:
            self.logger.warning(
                "Stage {} is outside of ".format(stage) +
                "the range of this cross section")
            return self._xs.conveyance(stage)

        return self._sect.conveyance(stage)

    @classmethod
    def from_csv(cls, csv_path):

        logger.debug("Initializing {} from {}".format(cls.__name__, csv_path))

        station, elevation = np.loadtxt(
            csv_path, delimiter=',', skiprows=1, unpack=True)

        # roughness isn't used here
        xs = AnchovyXS(station, elevation, 0.035, wall=True)

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

    def table_to_csv(self, csv_path):
        """Write the hydraulic property table contained
        in this instance to a CSV file

        Parameters
        ----------
        csv_path : str
            Path to save CSV file

        """

        self._sect.to_csv(csv_path)

    def top_width(self, stage):
        """Computes the top width for this cross section at a given stage

        Parameters
        ----------
        stage : float

        Returns
        -------
        float

        """

        if not np.isfinite(stage):
            self.logger.warning("Non-finite stage passed to top width method")

        if stage < self._e_min or self._e_max < stage:
            self.logger.warning(
                "Stage {} is outside of ".format(stage) +
                "the range of this cross section")
            return self._xs.top_width(stage)

        return self._sect.top_width(stage)

    def vel_dist_factor(self, stage):

        if not np.isfinite(stage):
            self.logger.warning(
                "Non-finite stage passed to vel_dist_factor method")

        if stage < self._e_min or self._e_max < stage:
            self.logger.warning(
                "Stage {} is outside of ".format(stage) +
                "the range of this cross section")
            return self._xs.vel_dist_factor(stage)

        return self._sect.vel_dist_factor(stage)

    def wetted_perimeter(self, stage):

        if not np.isfinite(stage):
            self.logger.warning(
                "Non-finite stage passed to wetted_perimeter method")

        if stage < self._e_min or self._e_max < stage:
            self.logger.warning(
                "Stage {} is outside of ".format(stage) +
                "the range of this cross section")
            return self._xs.wetted_perimeter(stage)

        return self._sect.wetted_perimeter(stage)
