# (C) Copyright 2021-2022 UCAR
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

from padme.core.plotter import DataHandler
from ..matplotlib_base import MatplotlibBase, Data

import matplotlib.pyplot as plt # type: ignore

class BasicLine(DataHandler):
    def is_valid(self, data: Data) -> bool:
        return super().is_valid(data)

    def process(self, data: Data, plot: 'OneDimensional') -> Data:
        super().process(data, plot)
        vars = data.variables
        v = list(vars.keys())[0]
        e = list(vars[v].data_vars.keys())[0]
        y = vars[v].data_vars[e]
        x = next(iter(data._coords.values()))
        print(v)
        xy = (x,y)
        plot.ax.plot(*xy)
        data.remove_variable(v)
        return data


class FilledLine(DataHandler):
    def is_valid(self, data: Data) -> bool:
        return False
        return super().is_valid(data)

    def process(self, data: Data, plot: 'OneDimensional') -> Data:
        return super().process(data, plot)


class OneDimensional(MatplotlibBase, factory_name="1d"):

    data_handlers = [
        FilledLine,
        BasicLine,
        *MatplotlibBase.data_handlers ]

    def __init__(self, data: Data):
        super().__init__(data)

    @classmethod
    def is_valid(cls, data: Data) -> bool:
        return (
            super().is_valid(data)
            and len(data.dimensions) == 1 )

    def _pre_plot(self) -> None:
        super()._pre_plot()

    def _post_plot(self) -> None:
        super()._post_plot()