# (C) Copyright 2021-2022 UCAR
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

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
    raise NotImplementedError()