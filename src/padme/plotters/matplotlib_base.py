# (C) Copyright 2021-2022 UCAR
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

from ..core.plotter import PlotterBase, Data

import matplotlib.pyplot as plt # type: ignore

class MatplotlibBase(PlotterBase, abstract=True):

    data_handlers = [
        *PlotterBase.data_handlers ]

    def __init__(self, data: Data):
        super().__init__(data)

    @classmethod
    def is_valid(cls, data: Data) -> bool:
        # we can't handle animations, yet.
        return (
            super().is_valid(data) and
            data.ndims <= 2 )

    def _pre_plot(self) -> None:
        self.fig = plt.figure()
        super()._pre_plot()

    def _post_plot(self) -> None:
        super()._post_plot()

    def _save(self, filename: str) -> None:
        plt.savefig(filename)
        plt.close(self.fig)
        super()._save(filename)