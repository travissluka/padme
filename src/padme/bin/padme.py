# (C) Copyright 2021-2022 UCAR
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

import click

from .autoplot import autoplot
from .plot import plot
from .parameters import parameters

@click.group()
@click.version_option()
def cli():
    """Plotting tools for Analysis, Diagnostics, Monitoring, and Evaluation.

    Joint Center for Satellite Data Assimilation (JCSDA) ©2022

    Tools for plotting JEDI diagnostics.
    """
    pass

cli.add_command(autoplot)
cli.add_command(plot)
cli.add_command(parameters)