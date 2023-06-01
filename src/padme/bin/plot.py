# (C) Copyright 2022-2022 UCAR
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

import click
import padme

@click.command()
@click.argument('input_file',
    type=click.Path(exists=True, dir_okay=False))
@click.option('--domain', default='global',
    type=click.Choice(padme.plotters.two_dimensional.latlon.domains.keys()),
    help="The domain used for any latlon plots")
@click.option('-ds', '--dim_select',
    multiple=True,
    help="Select a slice of the specified dimension. Format: \"<dim_name>:<value\"")
@click.option('-dc', '--dim_collapse',
    multiple=True,
    help="Collapse the specified dimension. Format: \"<dim_name>\"")
@click.option('-o', '--output',
    type=click.Path(writable=True), required=True, help="output filename")
@click.option('-d', '--diagnostic', default="ObsValue:mean")
@click.option('-p', '--param',
    multiple=True,
    help=("optional <key>:<value> plotting parameter. Run 'padme parameters' to see the list of"
         " valid parameters and their defaults"))
def plot(input_file, output, diagnostic, domain,
         dim_select, dim_collapse, param):
    """Plot a single plot """

    # set options
    plot_parameters = {
        'domain': domain,
    }
    for p in param:
        k,v = p.split(':')
        plot_parameters[k] = v

    # TODO, at some point we'll want to plot multiple diagnostics
    diag = diagnostic.split(':')[0]
    stat = diagnostic.split(':')[1]
    if 'title' not in plot_parameters:
        plot_parameters['title'] = f'{diag} {stat}'

    # get data
    opts={
        'diagnostic': diag,
        'statistic': (stat,),
        'ignore_missing': True }
    select = {s.split(':')[0]: s.split(':')[1] for s in dim_select}
    data = padme.DataAdapter('bespin',
        filename=input_file,
        select=select, collapse = dim_collapse,
        variables=opts)

    # get the plotter
    plotter = padme.Plotter(data=data, plot_parameters=plot_parameters)

    # set specific plotting parameters depending on what we are plotting
    # TODO this is hacky, find a cleaner way to do it.
    #  Assign attributes to the data xarray?
    if data.diff_name is not None:
        data.divergent = True
    if isinstance(plotter, padme.plotters.two_dimensional.TwoDimensional):
        if diag in ('OmB', 'OmA') and stat == 'mean':
            data.divergent = True


    # plot
    plotter.plot(data=data, filename=output)