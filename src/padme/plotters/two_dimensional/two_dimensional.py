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

    def process(self, data: Data, plot: 'TwoDimensional') -> Data:
        super().process(data, plot)
        vars = data.variables
        v = list(vars.keys())[0]
        e = list(vars[v].data_vars.keys())[0]
        d = vars[v].data_vars[e]

        y = d.coords['latitude'].data
        x = d.coords['longitude'].data
        z = d.data
        plot.ax.pcolormesh(
            x, y, d, transform=plot.transform
        )

        data.remove_variable(v)
        return data



class Contour(DataHandler):
    def is_valid(self, data: Data) -> bool:
        return super().is_valid(data)

    def process(self, data: Data, plot: 'TwoDimensional') -> Data:
        super().process(data, plot)
        vars = data.variables
        v = list(vars.keys())[0]
        data.remove_variable(v)
        return data


class TwoDimensional(MatplotlibBase, factory_name="2d"):

    data_handlers = [
        ColorMesh,
        Contour,
        *MatplotlibBase.data_handlers ]

    def __init__(self, data: Data):
        super().__init__(data)
        self.transform = None

    @classmethod
    def is_valid(cls, data: Data) -> bool:
        return (
            super().is_valid(data)
            and len(data.dimensions) == 2
            and len(data.datasets) == 1 )

    def _pre_plot(self) -> None:
        super()._pre_plot()

    def _post_plot(self) -> None:
        super()._post_plot()
