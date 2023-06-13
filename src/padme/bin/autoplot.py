# (C) Copyright 2021-2022 UCAR
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# TODO this all is "temporary" for use during initial dev, needs to be
# cleaned up

import click
import padme

def plot_all(data: padme.Data, filename_pfx: str, plot_parameters: dict, **kwargs):
    # for each variable / statistic
    keys = [str(v).split(".") for v in data.variables.keys()]
    for v in set([v[0] for v in keys]):
        # filter out raw "count" diagnostic
        p2 = [k[1:] for k in keys if k[0] == v and len(k) > 2]
        for diag in p2:
            name = '.'.join( (v, *diag) )
            d = data.get_variables( name )
            plotter = padme.Plotter(data=d, plot_parameters=plot_parameters)
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
                if diag[0] in ('OmB', 'OmA') and diag[1] == 'mean':
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
@click.option('-s', '--dim_select',
    multiple=True,
    help="Select a slice of the specified dimension. Format: \"<dim_name>:<value\"")
@click.option('-c', '--dim_collapse',
    multiple=True,
    help="Collapse the specified dimension. Format: \"<dim_name>\"")
@click.argument('input_files',
    type=click.Path(exists=True, dir_okay=False),
    nargs=-1, required=True)
def autoplot(input_files, output, diff, domain, dim_select, dim_collapse, format='bespin'):
    """Bespin Autoplot - Generate as many plots as possible from a given file."""


    # set options
    plot_parameters = {
        'domain': domain
        # TODO get other options from the command line
    }

    # read in data
    select = {s.split(':')[0]: s.split(':')[1] for s in dim_select}
    data = None
    data0 = None  # the control dataset when doing diff plots
    for input_file in input_files:
        data2 = padme.DataAdapter(format, filename=input_file,
            collapse=dim_collapse,
            select=select,
            variables={'statistic':( 'count', 'mean', 'stddev', 'rmsd')})

        if diff:
            if data0 is None:
                data0 = data2
            else:
                if data is not None:
                    raise NotImplementedError('calc diff of >1 exp')
                data = data2 - data0
        else:
            if data is not None:
                raise NotImplementedError('exp >1 if not diff')
            data = data2

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

            plot_all(data_channel, output, plot_parameters, ch=ch)
    else:
        plot_all(data, output, plot_parameters)