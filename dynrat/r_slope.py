"""computation of the ratio of flood wave slope to bed slope

References
----------
.. [1] Fread, D.L., 1973, A dynamic model of stage-discharge
   relations affected by changing discharge: NOAA Technical
   Memorandum NWS HYDRO-16, 55 p.
   http://repository.library.noaa.gov/view/noaa/13480

"""

import numpy as np
import pantherapy.panthera as sect


def r_slope(h_o, h_p, Q_o, Q_p, S_o, sect, t_diff):  

   """r=So/Sw

   Parameters
   ----------
   h_o : float
   h_p : float
   Q_o : float
   Q_p : float
   S_o : float
   sect : CrossSection
   t_diff : float
   
   """
   
   a_o = sect.area(h_o)
   a_p = sect.area(h_p)
   a_mean = (a_o + a_p)/2
   
   h_diff = h_p-h_o
   q_sum = Q_p+Q_o
   r1 = (56200*q_sum)/(h_diff*a_mean)
   r2  = r1*t_diff*S_o
   return r2


