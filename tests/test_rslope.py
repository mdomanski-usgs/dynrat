import os
import unittest
from unittest import TestCase

import numpy as np

from anchovy.crosssection import CrossSection

import dynrat
from dynrat.rslope import r_slope

current_path = os.path.dirname(os.path.realpath(__file__))
examples_dir = os.path.relpath(os.path.join(current_path, '..', 'examples'))


class TestRSlope(TestCase):

    def test_r_slope(self):

        xs_data_path = os.path.join(examples_dir, 'data', 'stlms', 'xs.csv')

        roughness = 0.035
        station, elevation = np.loadtxt(
            xs_data_path, delimiter=',', skiprows=1, unpack=True)
        datum = 379.58
        elevation = elevation - datum
        sect = CrossSection(station, elevation, roughness)

        h_o = 4.68  # stage prior to start of typical flood
        h_p = 24.18  # peak stage of typical flood
        q_o = 129000  # flow prior to typical flood
        q_p = 396000  # peak flow of typical flood
        t_diff = 7.58  # elapsed time of stage rise to peak stage in days

        bed_slope = 0.00011

        slope_ratio = r_slope(h_o, h_p, q_o, q_p, bed_slope, sect, t_diff)
        expected = 20.57622007239142

        self.assertAlmostEqual(expected, slope_ratio)


if __name__ == '__main__':
    unittest.main()
