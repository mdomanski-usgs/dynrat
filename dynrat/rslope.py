"""Computation of the ratio of channel bed slope to an average wave slope

References
----------
.. [1] Fread, D.L., 1973, A dynamic model of stage-discharge
   relations affected by changing discharge: NOAA Technical
   Memorandum NWS HYDRO-16, 55 p.
   http://repository.library.noaa.gov/view/noaa/13480

"""

import numpy as np
import pantherapy.panthera as sect


def r_slope(h_o, h_p, q_o, q_p, s_o, sect, t_diff):
    """Computes the ratio of channel bed slope to an average wave slope

    The ratio is computed according to eq. 13 of [1]_.

    .. math:: r = \\frac{S_o}{S_w}

    Parameters
    ----------
    h_o: float
        Stage at beginning of typical flood, in ft
    h_p: float
        Peak stage of typical flood, in ft
    q_o: float
        Discharge at beginning of typical flood, in cfs
    q_p: float
        Peak discharge for typical flood, in cfs
    s_o: float
        Bed slope
    sect: Sect
        Channel cross section
    t_diff: float
        Interval of time from beginning of rise in stage until the occurrence
        of peak stage, in days

    Returns
    -------
    float
        Ratio of channel bed slope to an average wave slope

    """

    h_mean = (h_o + h_p)/2

    a_mean = sect.area(h_mean)

    h_diff = h_p-h_o
    q_sum = q_p+q_o
    r1 = (56200*q_sum)/(h_diff*a_mean)
    r2 = r1*t_diff*s_o

    return r2
