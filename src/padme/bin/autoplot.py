# (C) Copyright 2021-2022 UCAR
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# TODO this all is "temporary" for use during initial dev, needs to be
# cleaned up

import click
import padme

def plot_all(data: padme.Data, filename_pfx: str, **kwargs):
    # for each variable / statistic
    keys = [str(v).split(".") for v in data.variables.keys()]
    for v in set([v[0] for v in keys]):
        # filter out raw "count" diagnostic
        p2 = [k[1:] for k in keys if k[0] == v and len(k) > 2]
        for diag in p2:
            name = '.'.join( (v, *diag) )
            d = data.get_variables( name )
            plotter = padme.Plotter(d)
            filename_components = [
                filename_pfx, v,
                None if 'ch' not in kwargs else f'ch{kwargs["ch"]}',
                *diag, 'jpg']
            filename='.'.join( [f for f in filename_components if f is not None] )
            print(f'Plotting {filename}')

            # set specific plotting parameters depending on what we are plotting
            # TODO this is hacky, find a cleaner way to do it.
            #  Assign attributes to the data xarray?
            if d.diff_name is not None:
                d.divergent = True
            if isinstance(plotter, padme.plotters.two_dimensional.TwoDimensional):
                if diag[0] in ('ombg', 'oman') and diag[1] == 'mean':
                    cm = padme.plotters.two_dimensional.two_dimensional.ColorMesh
                    d.divergent = True

            # generate plot
            plotter.plot(d, filename= filename)


@click.command()
@click.option('-o', '--output',
    type=click.Path(writable=True),
    required=True, help="prefix for output files",)
@click.option('--diff', is_flag=True, help=(
    "Difference plots: the first input file is subtracted from all the"
    " others."),)
@click.option('--domain', default='global',
    type=click.Choice(padme.plotters.two_dimensional.latlon.domains.keys()),
    help="The domain used for any latlon plots")
@click.argument('input_files',
    type=click.Path(exists=True, dir_okay=False),
    nargs=-1, required=True)
def autoplot(input_files, output, diff, domain, format='bespin'):
    """Bespin Autoplot - Generate as many plots as possible from a given file."""

    # warnings for things not yet implemented
    if len(input_files) > 1:
        raise NotImplementedError("can only handle one input file currently")
    if diff:
        raise NotImplementedError("Diff plots not yet implemented")

    # set options
    # TODO find a better way, we shouldn't directly access plotter classes here
    padme.plotters.two_dimensional.LatLon.domain = domain

    # read in data
    data = padme.DataAdapter(format, filename=input_files[0],
        variables={'statistic':( 'count', 'mean', 'stddev', 'rmsd')})

    # TODO split qc dimensions

    # if input data is multichannel 2D, process one channel at a time
    if len(data.dimensions) == 3 and 'sensor_channel' in data.dimensions:
        dims = data.dimensions
        del data
        for ch in dims['sensor_channel'].data:
            data_channel = padme.DataAdapter(
                format, filename=input_files[0], select={'sensor_channel':ch},
                variables={
                    'statistic':( 'count', 'mean', 'stddev', 'rmsd')})

            plot_all(data_channel, output, ch=ch)
    else:
        plot_all(data, output)