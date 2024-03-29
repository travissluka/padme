# (C) Copyright 2021-2022 UCAR
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

from padme.core.plotter import Parameters, Parameter, DataHandler
from ..matplotlib_base import MatplotlibBase, Data

import numpy as np
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

        # TODO remove hardcoded lat/lons
        # prepare data to plot
        y = d.coords['latitude'].data
        x = d.coords['longitude'].data
        z = d.data

        # annotations for the data min/max
        # TODO move this to a higher level? it's probably used
        # by many other data handlers.
        plot.annotations.append(
            f'min: {np.nanmin(z):.2f}  mean: {np.nanmean(z):.2f}  max: {np.nanmax(z):.2f}')

        # determine the color range
        # TODO, allow user to override
        vmin, vmax = self.calc_auto_range(z, plot.parameters['range_pct'])
        cmap = plot.parameters['mesh.cmap']
        if data.divergent:
            # TODO "divergent" should be moved to a per variable level?
            vmax = max(abs(vmin), vmax)
            vmin = -vmax
            cmap = plot.parameters['mesh.cmap_div']

        # plot !
        mesh = plot.ax.pcolormesh(
            x, y, d,
            transform=plot.transform,
            vmin=vmin, vmax=vmax,
            cmap = cmap
        )

        # colorbar
        plot.fig.colorbar(mesh, ax=plot.ax,
            orientation='vertical',
            shrink=0.7,
            fraction=0.08)

        data.remove_variable(v)
        return data

    @classmethod
    def calc_auto_range(cls, data, pct: float = 0.99):
        """Automatically calculate a color range that covers "pct" of the values."""
        assert(0 < pct <= 1.0)
        auto_range = np.nanpercentile(
            data,
            [100*(1.0-pct)/2.0,
             100*((1.0-pct)/2.0 + pct)])
        return auto_range


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

    parameters = Parameters(
        MatplotlibBase.parameters,
        Parameter('mesh.cmap', 'viridis', 'filled colormap color'),
        Parameter('mesh.cmap_div', 'RdBu_r', 'filled colormap for divergent plots'),
        Parameter('range_pct', 0.99, 'auto color range percentile')
        )

    def __init__(self, data: Data, **kwargs):
        super().__init__(data, **kwargs)
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
