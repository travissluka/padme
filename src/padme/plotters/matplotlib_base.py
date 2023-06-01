# (C) Copyright 2021-2022 UCAR
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

from ..core.plotter import Parameter, Parameters, PlotterBase, Data

import matplotlib.pyplot as plt # type: ignore

class MatplotlibBase(PlotterBase, abstract=True):

    data_handlers = [
        *PlotterBase.data_handlers ]

    parameters = Parameters(
        PlotterBase.parameters,
        Parameter('title', '', 'plot title'),
        Parameter('fig_width', 8, 'width of the figure, in inches'),
        Parameter('fig_height', 4.8, 'height of the figure in inches')
    )

    def __init__(self, data: Data, **kwargs):
        super().__init__(data, **kwargs)
        self.projection = None
        self.annotations = []

        # common annotations
        dt = data.datetime
        self.annotations.append(f'datetime: {dt[0]}  to  {dt[1]}')

    @classmethod
    def is_valid(cls, data: Data) -> bool:
        # we can't handle animations, yet.
        return (
            super().is_valid(data) and
            len(data.dimensions) <= 2 )

    def _pre_plot(self) -> None:
        # TODO smartly calculate desired size
        w=self.parameters['fig_width']
        h=self.parameters['fig_height']

        self.fig = plt.figure(figsize=(w,h))
        self.ax_outer = self.fig.add_gridspec(2,1, height_ratios=[0.9,0.1],)
        self.ax = self.fig.add_subplot(self.ax_outer[0], projection=self.projection)
        self.ax_bottom = self.fig.add_subplot(self.ax_outer[1])
        self.ax_bottom.axis('off')

        super()._pre_plot()

    def _post_plot(self) -> None:
        super()._post_plot()

        # title, axis labels
        self.ax.set_title(self.parameters['title'])

        # write the annotations at the bottom
        fontsize = 10
        x0 = fontsize
        x1 = self.fig.get_figwidth()*72 - fontsize
        y0 = 0
        y1 = self.ax_bottom.get_window_extent().transformed(self.fig.dpi_scale_trans.inverted()).y1*72 - fontsize
        y = y1
        for a in self.annotations:
            self.ax_bottom.annotate(a, xy=(x0, y), xycoords='figure points',
                verticalalignment='top', weight='light', fontsize=fontsize)
            y -= (fontsize+2)

        # TODO, need to take a closer look at how layout is being done
        plt.tight_layout(pad=0.1)

    def _save(self, filename: str) -> None:
        plt.savefig(filename)
        plt.close(self.fig)
        super()._save(filename)