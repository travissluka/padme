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
        self.projection = None

    @classmethod
    def is_valid(cls, data: Data) -> bool:
        # we can't handle animations, yet.
        return (
            super().is_valid(data) and
            len(data.dimensions) <= 2 )

    def _pre_plot(self) -> None:
        self.fig = plt.figure()
        self.ax_outer = self.fig.add_gridspec(2,1, height_ratios=[0.9,0.1],)
        self.ax = self.fig.add_subplot(
            self.ax_outer[0],
            projection=self.projection,
        )
        super()._pre_plot()

    def _post_plot(self) -> None:
        plt.annotate(self._factory_name,(10,10), xycoords='figure points')
        super()._post_plot()

    def _save(self, filename: str) -> None:
        plt.savefig(filename)
        plt.close(self.fig)
        super()._save(filename)