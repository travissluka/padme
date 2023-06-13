# (C) Copyright 2021-2022 UCAR
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

from padme.core.plotter import DataHandler
from ..matplotlib_base import MatplotlibBase, Data

import matplotlib.pyplot as plt # type: ignore


class Categorical(MatplotlibBase, factory_name="categorical"):

    data_handlers = [
        *MatplotlibBase.data_handlers ]

    def __init__(self, data: Data):
        super().__init__(data)

    @classmethod
    def is_valid(cls, data: Data) -> bool:
        return (
            super().is_valid(data)
            and not len(data.dimensions) )

    def _pre_plot(self) -> None:
        super()._pre_plot()

    def _post_plot(self) -> None:
        super()._post_plot()