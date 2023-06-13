# (C) Copyright 2022-2022 UCAR
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

import click
import padme

@click.command()
def parameters():
    """display the default plotting parameters."""
    for c in padme.PlotterBase.get_valid_classes():
        if '_factory_name' not in c.__dict__:
            continue

        parent = c.mro()[1]
        if '_factory_name' in parent.__dict__:
            parent = parent._factory_name
        else:
            parent = None

        print("")
        print("")
        print( f'{c._factory_name}  (inherits from: {parent})')
        print('--------------------------------------')
        keys = sorted(list(c.parameters.keys()))
        for k in keys:
            print(c.parameters.get(k))

    pass