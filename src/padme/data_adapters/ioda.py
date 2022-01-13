# (C) Copyright 2021-2022 UCAR
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

from ..core.data_adapter import register_data_adapter, Data


@register_data_adapter(name='ioda')
def ioda_adapter(
        filename: str) -> Data:
    raise NotImplementedError()