# (C) Copyright 2021-2022 UCAR
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

import xarray as xr

from ..core.data_adapter import register_data_adapter, Data

try:
    import bespin
    bespin_found = True
except ModuleNotFoundError as e:
    bespin_found = False


@register_data_adapter(name='bespin')
def bespin_adapter(
        filename: str,
        select=None,
        collapse=None,
        variables=None) -> Data:
    if not bespin_found:
        raise ModuleNotFoundError(
            f'Cannot use "bespin_file" if "bespin" is not installed.')

    # read in the file
    exp_name = "EXP1" # TODO correctly specify the experiment name
    bs = bespin.BinnedStatistics.read(filename)

    # extra processing (e.g. select a slice of a dimension, or collapse a dim)
    if select is not None:
        bs = bs.select_dim(**select)
    if collapse is not None:
        bs = bs.collapse_dim(*collapse)

    # get the requested statistical variables (or all if none specified)
    if variables is None:
        variables = {}
    data = bs.get(**variables)

    # TODO, messy, get bespin to return what is directly needed.
    coord_edges = [b.edges_to_xarray().coords[b.name] for b in bs.bins]
    coords = None
    if ('sensor_channel' in bs._data.coords
            and 'sensor_channel' not in {b.name for b in bs.bins}):
        coords = (bs._data.coords['sensor_channel'],)
    return Data(name=exp_name, data=data, coord_edges=coord_edges, coords=coords)

