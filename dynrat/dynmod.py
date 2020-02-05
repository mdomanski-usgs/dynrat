import numpy as np


class Frict:
    """Linearly interpolates Manning's n

    `stage` and `roughness` must be one-dimensional and have two elements
    or more. `stage` must be sorted in ascending order.

    Parameters
    ----------
    stage : array_like
        Water surface elevations
    roughness : array_like
        Manning's n values

    """

    def __init__(self, stage, roughness):

        self._stage = np.array(stage)
        self._roughness = np.array(roughness)

        if self._stage.ndim != 1:
            raise ValueError("stage must be one-dimensional")

        if self._stage.size < 2:
            raise ValueError("stage must at least have two elements")

        if not np.alltrue(np.diff(stage) > 0)):
            raise ValueError("stage must be sorted in ascending order")

        if self._roughness.ndim != 1:
            raise ValueError("roughness must be one-dimensional")

        if self._roughness.size < 2:
            raise ValueError("roughness must at least have two elements")

        if self._stage.size != self._roughness.size:
            raise ValueError("stage and roughness must have the same size")

    def roughness(self, stage):
        """Computes Manning's n for a particular elevation of the
        water surface.

        Parameters
        ----------
        stage : array_like
            Water surface elevation

        Returns
        -------
        float or ndarray
            Manning's n

        """

        return np.interp(stage, self._stage, self._roughness)


class Sect:

    def __init__(self):

        pass


class QSolve:

    def __init__(
            self,
            sect,
            frict,
            bed_slope,
            slope_ratio,
            time_step,
            epsilon):

        pass
