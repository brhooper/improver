# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# (C) British Crown copyright. The Met Office.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
"""Unit tests for the "cube_manipulation.normalise_to_reference" function."""
import iris
import numpy as np
import pytest

from improver.synthetic_data.set_up_test_cubes import set_up_percentile_cube
from improver.utilities.forecast_reference_enforcement import normalise_to_reference


@pytest.fixture
def shape():
    """Define shape of all cubes used in these tests."""
    output = (2, 3, 3)
    return output


@pytest.fixture()
def percentiles():
    """Define the percentiles of all cubes used in these tests."""
    return [40.0, 60.0]


@pytest.fixture
def input_cubes(shape, percentiles):
    """Create cubelist used as input for tests."""
    rain_data = 0.5 * 4 * np.ones(shape, dtype=np.float32)
    sleet_data = 0.4 * 4 * np.ones(shape, dtype=np.float32)
    snow_data = 0.1 * 4 * np.ones(shape, dtype=np.float32)

    for data in [rain_data, sleet_data, snow_data]:
        data[1, :, :] = 1.5 * data[1, :, :]

    rain_cube = set_up_percentile_cube(
        rain_data, percentiles, name="rainfall_rate", units="m s-1"
    )
    sleet_cube = set_up_percentile_cube(
        sleet_data, percentiles, name="lwe_sleetfall_rate", units="m s-1"
    )
    snow_cube = set_up_percentile_cube(
        snow_data, percentiles, name="lwe_snowfall_rate", units="m s-1"
    )

    return iris.cube.CubeList([rain_cube, sleet_cube, snow_cube])


@pytest.fixture
def reference_cube(shape, percentiles):
    """Create reference cube used as input for tests."""
    precip_data = 8 * np.ones(shape, dtype=np.float32)
    precip_data[1, :, :] = 1.5 * precip_data[1, :, :]

    return set_up_percentile_cube(
        precip_data, percentiles, name="lwe_precipitation_rate", units="m s-1"
    )


@pytest.fixture()
def expected_cubes(shape, percentiles):
    """Create cubelist containing expected outputs of tests."""
    rain_data = 0.5 * 8 * np.ones(shape, dtype=np.float32)
    sleet_data = 0.4 * 8 * np.ones(shape, dtype=np.float32)
    snow_data = 0.1 * 8 * np.ones(shape, dtype=np.float32)

    for data in [rain_data, sleet_data, snow_data]:
        data[1, :, :] = 1.5 * data[1, :, :]

    rain_cube = set_up_percentile_cube(
        rain_data, percentiles, name="rainfall_rate", units="m s-1"
    )
    sleet_cube = set_up_percentile_cube(
        sleet_data, percentiles, name="lwe_sleetfall_rate", units="m s-1"
    )
    snow_cube = set_up_percentile_cube(
        snow_data, percentiles, name="lwe_snowfall_rate", units="m s-1"
    )

    return iris.cube.CubeList([rain_cube, sleet_cube, snow_cube])


def test_basic(input_cubes, reference_cube, expected_cubes):
    """Test basic usage that the input cubes are updated correctly."""
    output = normalise_to_reference(input_cubes, reference_cube)
    output_sum = output[0].data + output[1].data + output[2].data

    assert output == expected_cubes
    assert np.array_equal(output_sum, reference_cube.data)


@pytest.mark.parametrize("ignore_zero_total", (True, False))
def test_zero_total(input_cubes, reference_cube, expected_cubes, ignore_zero_total):
    """Test cubes are updated correctly when some values in input_cubes are zero in
    all input cubes.
    """
    for index in range(len(input_cubes)):
        input_cubes[index].data[0, :, :] = 0.0
        expected_cubes[index].data[0, :, :] = 0.0

    if not ignore_zero_total:
        with pytest.raises(
            ValueError, match="There are instances where the total of input"
        ):
            normalise_to_reference(input_cubes, reference_cube, ignore_zero_total)
    else:
        output = normalise_to_reference(input_cubes, reference_cube, ignore_zero_total)
        output_sum = output[0].data + output[1].data + output[2].data

        reference_with_zeroes = reference_cube.copy()
        reference_with_zeroes.data[0, :, :] = 0.0

        assert output == expected_cubes
        assert np.array_equal(output_sum, reference_with_zeroes.data)


def test_single_input_cube(input_cubes, reference_cube, expected_cubes):
    """Test cube is updated correctly when the input cubelist contains only one cube."""
    input_cube = input_cubes[0]
    output = normalise_to_reference(iris.cube.CubeList([input_cube]), reference_cube)

    # check that metadata is as expected
    assert input_cube == output[0].copy(data=input_cube.data)
    # check that data is as expected
    assert np.array_equal(output[0].data, reference_cube.data)


def test_n_coords_mismatch(input_cubes, reference_cube):
    reference_cube = reference_cube[0, :, :]

    with pytest.raises(ValueError, match="The number of dimensions in input cubes"):
        normalise_to_reference(input_cubes, reference_cube)


def test_coord_values_mismatch(input_cubes, reference_cube):
    reference_cube.coord("percentile").points = np.array([50.0, 70.0], dtype=np.float32)

    with pytest.raises(
        ValueError, match="The dimension coordinates on the input cubes"
    ):
        normalise_to_reference(input_cubes, reference_cube)


def test_coord_names_mismatch(input_cubes, reference_cube):
    input_cubes[0].coord("percentile").rename("realizations")

    with pytest.raises(
        ValueError, match="The dimension coordinates on the input cubes"
    ):
        normalise_to_reference(input_cubes, reference_cube)