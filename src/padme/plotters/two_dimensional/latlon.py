# (C) Copyright 2021-2022 UCAR
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

import cartopy.crs as ccrs
from cartopy.mpl import gridliner
import matplotlib.pyplot as plt # type: ignore
import matplotlib.ticker as mticker

from .two_dimensional import TwoDimensional, Data

class LatLon(TwoDimensional, factory_name="latlon"):

    data_handlers = [
        *TwoDimensional.data_handlers ]

    def __init__(self, data: Data):
        super().__init__(data)
        self.projection = ccrs.Robinson()
        self.transform = ccrs.PlateCarree()

    @classmethod
    def is_valid(cls, data: Data) -> bool:
        return (
            super().is_valid(data)
            and data.dimensions.keys() == {'latitude', 'longitude'})

    def _post_plot(self) -> None:
        super()._post_plot()
        self.ax.coastlines(color='k', alpha=0.5)

        gl = self.ax.gridlines(alpha=0.5, color='gray', linestyle='--')

        # TODO smarter lat/lon ticks for regional plots
        gl.xformatter = gridliner.LONGITUDE_FORMATTER
        gl.xlocator = mticker.FixedLocator([-90, 0, 90, 180, 270])
        gl.yformatter = gridliner.LATITUDE_FORMATTER
        gl.ylocator = mticker.FixedLocator([-90, -60, -30, 0, 30, 60, 90])
