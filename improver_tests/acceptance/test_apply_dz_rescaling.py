# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'IMPROVER' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
"""
Tests for the apply-dz-rescaling CLI
"""

import pytest

from . import acceptance as acc

pytestmark = [pytest.mark.acc, acc.skip_if_kgo_missing]
CLI = acc.cli_name_with_dashes(__file__)
run_cli = acc.run_cli(CLI)


def test_apply_dz_rescaling(tmp_path):
    """Test apply_dz_rescaling CLI."""
    kgo_dir = acc.kgo_root() / "apply-dz-rescaling/"
    kgo_path = kgo_dir / "kgo.nc"
    forecast_path = kgo_dir / "20230220T1200Z-PT0006H00M-wind_speed_at_10m.nc"
    scaled_dz_path = kgo_dir / "scaled_dz.nc"
    output_path = tmp_path / "output.nc"
    args = [forecast_path, scaled_dz_path, "--output", output_path]
    run_cli(args)
    acc.compare(output_path, kgo_path)
