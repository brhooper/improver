# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'IMPROVER' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
"""Convert NetCDF files to realizations."""

from improver import cli


@cli.clizefy
@cli.with_output
def process(
    cube: cli.inputcube,
    raw_cube: cli.inputcube = None,
    *,
    realizations_count: int = None,
    random_seed: int = None,
    tie_break: str = "random",
    ignore_ecc_bounds_exceedance: bool = False,
    skip_ecc_bounds: bool = False,
):
    """Converts an incoming cube into one containing realizations.

    Args:
        cube (iris.cube.Cube):
            A cube to be processed.
        raw_cube (iris.cube.Cube):
            Cube of raw (not post processed) weather data.
            If this argument is given ensemble realizations will be created
            from percentiles by reshuffling them in correspondence to the rank
            order of the raw ensemble. Otherwise, the percentiles are rebadged
            as realizations.
        realizations_count (int):
            The number of ensemble realizations in the output.
        random_seed (int):
            Option to specify a value for the random seed when reordering percentiles.
            This value is for testing purposes only, to ensure reproduceable outputs.
            It should not be used in real time operations as it may introduce a bias
            into the reordered forecasts.
        tie_break (str):
            Option to specify the tie breaking method when reordering percentiles.
            The available methods are "random", to tie-break randomly, and
            "realization", to tie-break by assigning values to the highest numbered
            realizations first.
        ignore_ecc_bounds_exceedance (bool):
            If True where percentiles (calculated as an intermediate output
            before realization) exceed the ECC bounds range, raises a
            warning rather than an exception.
        skip_ecc_bounds (bool):
            If True, ECC bounds are not included either when percentiles are resampled
            as an intermediate step prior to creating realizations or when probabilities
            are converted to percentiles as an intermediate step prior to creating
            realizations. This has the effect that percentiles outside of the range
            given by the input percentiles will be computed by nearest neighbour
            interpolation from the nearest available percentile, rather than using
            linear interpolation between the nearest available percentile and
            the ECC bound.

    Returns:
        iris.cube.Cube:
            The processed cube.
    """
    from improver.ensemble_copula_coupling.ensemble_copula_coupling import (
        ConvertProbabilitiesToPercentiles,
        EnsembleReordering,
        RebadgePercentilesAsRealizations,
        ResamplePercentiles,
    )
    from improver.metadata.probabilistic import is_probability

    if cube.coords("realization"):
        return cube

    if not cube.coords("percentile") and not is_probability(cube):
        raise ValueError("Unable to convert to realizations:\n" + str(cube))

    if realizations_count is None:
        try:
            realizations_count = len(raw_cube.coord("realization").points)
        except AttributeError:
            # raised if raw_cube is None, hence has no attribute "coord"
            msg = "Either realizations_count or raw_cube must be provided"
            raise ValueError(msg)

    if cube.coords("percentile"):
        percentiles = ResamplePercentiles(
            ecc_bounds_warning=ignore_ecc_bounds_exceedance,
            skip_ecc_bounds=skip_ecc_bounds,
        )(cube, no_of_percentiles=realizations_count)
    else:
        percentiles = ConvertProbabilitiesToPercentiles(
            ecc_bounds_warning=ignore_ecc_bounds_exceedance,
            skip_ecc_bounds=skip_ecc_bounds,
        )(cube, no_of_percentiles=realizations_count)

    if raw_cube:
        result = EnsembleReordering()(
            percentiles, raw_cube, random_seed=random_seed, tie_break=tie_break
        )
    else:
        result = RebadgePercentilesAsRealizations()(percentiles)

    return result
