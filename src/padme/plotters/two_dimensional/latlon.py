# (C) Copyright 2021-2022 UCAR
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

import cartopy.crs as ccrs
from cartopy.mpl import gridliner
import matplotlib.pyplot as plt # type: ignore
import matplotlib.ticker as mticker
import yaml
import pathlib
import numpy

from .two_dimensional import TwoDimensional, Data, Parameter, Parameters

DOMAIN_CONFIG_FILE = (pathlib.Path(__file__).parent / '../../config/latlon_domains.yaml').resolve()
domains = yaml.safe_load(open(DOMAIN_CONFIG_FILE))


class LatLon(TwoDimensional, factory_name="latlon"):

    data_handlers = [
        *TwoDimensional.data_handlers ]

    parameters = Parameters(
        TwoDimensional.parameters,
        Parameter('domain', 'global', 'The regional domain for the plot'),
        Parameter('grid.spacing', 30, 'grid line spacing (degrees)'),
    )

    domain_configs = None # read in from config file when needed

    def __init__(self, data: Data, **kwargs):
        super().__init__(data, **kwargs)

        # determine domain specific parameters
        try:
            domain_config = domains[self.parameters['domain']]

            # projection
            projection_cls = ccrs.__dict__[domain_config['projection']]
            if 'projection opts' in domain_config:
                projection_opts = domain_config['projection opts']
            else:
                projection_opts = {}
            self.projection = projection_cls(**projection_opts)

            # plotting extents
            self.extent = None
            if 'extent'  in domain_config:
                self.extent = domain_config['extent']

        except Exception as e:
            print("ERROR while setting domain specific parameters.")
            print(f"Try checking the config file: {DOMAIN_CONFIG_FILE}")
            raise e

        self.transform = ccrs.PlateCarree()

    @classmethod
    def is_valid(cls, data: Data) -> bool:
        return (
            super().is_valid(data)
            and data.dimensions.keys() == {'latitude', 'longitude'})

    def _pre_plot(self) -> None:
        super()._pre_plot()
        if self.extent is not None:
            self.ax.set_extent(self.extent, crs=ccrs.PlateCarree())

    def _post_plot(self) -> None:
        super()._post_plot()
        self.ax.coastlines(color='k', alpha=0.5)

        gl = self.ax.gridlines(alpha=0.5, color='gray', linestyle='--')

        # TODO smarter lat/lon ticks for regional plots
        gl.xformatter = gridliner.LONGITUDE_FORMATTER
        gl.xlocator = mticker.FixedLocator(
            numpy.linspace(-180,180, round(360/self.parameters['grid.spacing'])+1))
        gl.yformatter = gridliner.LATITUDE_FORMATTER
        gl.ylocator = mticker.FixedLocator(
            numpy.linspace(-90,90, round(180/self.parameters['grid.spacing'])+1))

