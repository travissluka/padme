# (C) Copyright 2021-2022 UCAR
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

from padme.core.plotter import DataHandler
from ..matplotlib_base import MatplotlibBase, Data

import matplotlib.pyplot as plt # type: ignore

class ColorMesh(DataHandler):
    def is_valid(self, data: Data) -> bool:
        return (
            super().is_valid(data)
            and self.first_use )

class Contour(DataHandler):
    def is_valid(self, data: Data) -> bool:
        return super().is_valid(data)


class TwoDimensional(MatplotlibBase, factory_name="2d"):

    data_handlers = [
        ColorMesh,
        Contour,
        *MatplotlibBase.data_handlers ]

    def __init__(self, data: Data):
        super().__init__(data)

    @classmethod
    def is_valid(cls, data: Data) -> bool:
        # we can't handle animations, yet.
        return (
            super().is_valid(data)
            and data.ndims == 2
            and data.nexps == 1 )

    def _pre_plot(self) -> None:
        super()._pre_plot()

    def _post_plot(self) -> None:
        super()._post_plot()