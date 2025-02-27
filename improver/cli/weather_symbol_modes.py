# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'IMPROVER' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
"""CLI to generate modal categories over periods."""

from improver import cli


@cli.clizefy
@cli.with_output
def process(
    *cubes: cli.inputcube,
    decision_tree: cli.inputjson = None,
    broad_categories: cli.inputjson = None,
    wet_categories: cli.inputjson = None,
    intensity_categories: cli.inputjson = None,
    day_weighting: int = 1,
    day_start: int = 6,
    day_end: int = 18,
    wet_bias: int = 1,
    model_id_attr: str = None,
    record_run_attr: str = None,
):
    """Generates a modal weather code for the period covered by the input
    categorical cubes. Where there are different categories available
    for night and day, the modal code returned is always a day code, regardless
    of the times covered by the input files. The weather codes provided are expected
    to end at midnight and therefore represent either a full day or a partial day.

    Args:
        cubes (iris.cube.CubeList):
            A cubelist containing categorical cubes that cover the period
            over which a modal category is desired.
        decision_tree (dict):
            A JSON file containing a decision tree definition.
        broad_categories (dict):
            A JSON file containing a definition for a broad category grouping.
            The expected categories are wet and dry.
        wet_categories (dict):
            A JSON file containing a definition for a wet category grouping. No specific
            names for the keys are required. Key and values within the dictionary
            should both be ordered in terms of descending priority.
        intensity_categories (dict):
            A JSON file containing a definition for an intensity category grouping.
            Values should be ordered in terms of descending priority. The most common
            weather code from the options available representing different intensities
            will be used as the representative weather code.
        day_weighting:
            Weighting to provide day time weather codes. A weighting of 1 indicates
            the default weighting. A weighting of 2 indicates that the weather codes
            during the day time period will be duplicated, so that they count twice
            as much when computing a representative weather code.
        day_start:
            Hour defining the start of the daytime period.
        day_end:
            Hour defining the end of the daytime period.
        wet_bias:
            Bias to provide wet weather codes. A bias of 1 indicates the
            default, where half of the codes need to be a wet code,
            in order to generate a wet code. A bias of 3 indicates that
            only a quarter of codes are required to be wet, in order to generate
            a wet symbol. To generate a wet symbol, the fraction of wet symbols
            therefore need to be greater than or equal to 1 / (1 + wet_bias).
        model_id_attr (str):
            Name of attribute recording source models that should be
            inherited by the output cube. The source models are expected as
            a space-separated string.
        record_run_attr:
            Name of attribute used to record models and cycles used in
            constructing the categorical data.

    Returns:
        iris.cube.Cube:
            A cube of modal weather codes over a period.
    """
    from improver.categorical.modal_code import ModalFromGroupings

    if not cubes:
        raise RuntimeError("Not enough input arguments. See help for more information.")

    return ModalFromGroupings(
        decision_tree,
        broad_categories,
        wet_categories,
        intensity_categories,
        day_weighting,
        day_start,
        day_end,
        wet_bias,
        model_id_attr=model_id_attr,
        record_run_attr=record_run_attr,
    )(cubes)
