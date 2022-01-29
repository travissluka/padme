# (C) Copyright 2021-2022 UCAR
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

import click

import padme

@click.command()
@click.option('-o', '--output',
    type=click.Path(writable=True),
    required=True, help="prefix for output files",)
@click.option('--diff', is_flag=True, help=(
    "Difference plots: the first input file is subtracted from all the"
    " others."),)
@click.argument('input_files',
    type=click.Path(exists=True, dir_okay=False),
    nargs=-1, required=True)
def autoplot(input_files, output, diff, format='bespin'):
    """Generate as many plots as possible from a given file."""

    if len(input_files) > 1:
        raise NotImplementedError("can only handle one input file currently")

    data = padme.DataAdapter(format, filename=input_files[0])

    # if input data is multichannel 2D, process one channel at a time
    if len(data.dimensions) == 3 and 'sensor_channel' in data.dimensions:
        dims = data.dimensions
        del data
        for ch in dims['sensor_channel'].data:
            data_channel = padme.DataAdapter(
                format, filename=input_files[0], select={'sensor_channel':ch},
                variables={
                    'diagnostic':('ObsValue',),
                    'statistic':( 'mean', 'stddev')})

            plotter = padme.Plotter(data_channel)
            plotter.plot(data_channel, filename=f'foo_ch{ch}.jpg')