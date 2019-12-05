# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# (C) British Crown Copyright 2017-2019 Met Office.
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
"""Tests for the wind-gust-diagnostic CLI"""

import pytest

from improver.cli import wind_gust_diagnostic
from improver.tests import acceptance as acc


@pytest.mark.acc
@acc.skip_if_kgo_missing
def test_average_wind_gust(tmp_path):
    """Test basic wind gust diagnostic processing"""
    kgo_dir = acc.kgo_root() / "wind-gust-diagnostic/basic"
    kgo_path = kgo_dir / "kgo_average_wind_gust.nc"
    output_path = tmp_path / "output.nc"
    args = [str(kgo_dir / "wind_gust_perc.nc"),
            str(kgo_dir / "wind_speed_perc.nc"),
            str(output_path)]
    wind_gust_diagnostic.main(args)
    acc.compare(output_path, kgo_path)


@pytest.mark.acc
@acc.skip_if_kgo_missing
def test_extreme_wind_gust(tmp_path):
    """Test basic wind gust diagnostic processing"""
    kgo_dir = acc.kgo_root() / "wind-gust-diagnostic/basic"
    kgo_path = kgo_dir / "kgo_extreme_wind_gust.nc"
    output_path = tmp_path / "output.nc"
    args = ["--percentile_gust=95.0", "--percentile_ws=100.0",
            str(kgo_dir / "wind_gust_perc.nc"),
            str(kgo_dir / "wind_speed_perc.nc"),
            str(output_path)]
    wind_gust_diagnostic.main(args)
    acc.compare(output_path, kgo_path)