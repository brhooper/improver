# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'IMPROVER' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
"""Unit tests for plugin wind_downscaling.FrictionVelocity"""

import unittest

import numpy as np
from iris.tests import IrisTest

from improver.constants import RMDI
from improver.wind_calculations.wind_downscaling import FrictionVelocity


class Test_process(IrisTest):
    """Test the creation of friction velocity 2D arrays. Note that in the
    future, use of the Real Missing Data Indicator (RMDI) constant is due to be
    deprecated in favour of np.nan"""

    def setUp(self):
        """Creates wind-speed, height, veg roughness and mask 2D arrays."""

        n_x, n_y = 4, 4  # Set array dimensions.

        # Wind speed=u_href=10m/s  Height=h_ref=20m
        self.u_href = np.full([n_y, n_x], 10, dtype=float)
        self.h_ref = np.full([n_y, n_x], 20, dtype=float)
        # Vegetative roughness = 0.5m
        self.z_0 = np.full([n_y, n_x], 0.5, dtype=float)

        # Mask for land/sea - True for land-points, false for sea.
        self.mask = np.full([n_y, n_x], False, dtype=bool)
        # Mask has 'land' in centre bounded by sea points.
        self.mask[1 : n_y - 1, 1 : n_x - 1] = True

    def test_returns_expected_values(self):
        """Test that the function returns correct 2D array of floats."""

        # Equation is (K=0.4): ustar = K * (u_href / ln(h_ref / z_0))
        expected_out = np.array(
            [
                [RMDI, RMDI, RMDI, RMDI],
                [RMDI, 1.08434, 1.08434, RMDI],
                [RMDI, 1.08434, 1.08434, RMDI],
                [RMDI, RMDI, RMDI, RMDI],
            ]
        )

        result = FrictionVelocity(
            self.u_href, self.h_ref, self.z_0, self.mask
        ).process()

        self.assertIsInstance(result, np.ndarray)
        self.assertArrayAlmostEqual(result, expected_out)

    def test_handles_nan_values(self):
        """Test that the function accepts NaN values correctly."""

        self.u_href[1, 1] = np.nan  # Adds NaN value

        expected_out = np.array(
            [
                [RMDI, RMDI, RMDI, RMDI],
                [RMDI, np.nan, 1.08434, RMDI],
                [RMDI, 1.08434, 1.08434, RMDI],
                [RMDI, RMDI, RMDI, RMDI],
            ]
        )

        result = FrictionVelocity(
            self.u_href, self.h_ref, self.z_0, self.mask
        ).process()

        self.assertIsInstance(result, np.ndarray)
        self.assertArrayAlmostEqual(result, expected_out)

    def test_handles_zero_values(self):
        """Function calculates log(href/z_0) - test that the function accepts
        zero values in h_ref and z_0 and returns np.nan without crashing."""

        h_ref_zeros = np.full_like(self.h_ref, 0)
        z_0_zeros = np.full_like(self.z_0, 0)

        expected_out = np.array(
            [
                [RMDI, RMDI, RMDI, RMDI],
                [RMDI, np.nan, np.nan, RMDI],
                [RMDI, np.nan, np.nan, RMDI],
                [RMDI, RMDI, RMDI, RMDI],
            ]
        )

        result = FrictionVelocity(
            self.u_href, h_ref_zeros, z_0_zeros, self.mask
        ).process()

        self.assertIsInstance(result, np.ndarray)
        self.assertArrayAlmostEqual(result, expected_out)

    def test_handles_different_sized_arrays(self):
        """Test when if different size arrays have been input"""
        u_href = np.full([3, 3], 10, dtype=float)
        msg = "Different size input arrays u_href, h_ref, z_0, mask"
        with self.assertRaisesRegex(ValueError, msg):
            FrictionVelocity(u_href, self.h_ref, self.z_0, self.mask).process()

    def test_output_is_float32(self):
        """Test that the plugin returns an array of float 32 type
        even when the input arrays are double precision."""

        result = FrictionVelocity(
            self.u_href, self.h_ref, self.z_0, self.mask
        ).process()

        self.assertEqual(result.dtype, np.float32)


if __name__ == "__main__":
    unittest.main()
