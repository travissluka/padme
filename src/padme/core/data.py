# (C) Copyright 2021-2022 UCAR
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

from collections import OrderedDict
from typing import Dict, Hashable, Iterable,  Optional, Union
import copy
import numpy
import xarray

class Data:
    """Hold all the data that is to be plotted.

    Data can be accessed in two ways:
    1) all the variables organized by experiment (.datasets)
    2) all the experiments organized by variable (.variables)
    """

    def __init__(
            self,
            name: str,
            data: xarray.Dataset,
            coords: Optional[Iterable[xarray.DataArray]] = None,
            coord_edges: Optional[Iterable[xarray.DataArray]] = None,
    ):
        self.divergent = False # TODO move this to a per variable basis
        self.diff_name: Optional[Hashable] = None

        # error checking on input arguments
        if coords is None and coord_edges is None:
            raise ValueError(
                '"coords" and/or "coord_edges" must be defined')

        # TODO check their order based on what is stored in data
        self._data: OrderedDict[Hashable, xarray.Dataset] = (
            OrderedDict({name: data}))

        self._coords: OrderedDict[Hashable, xarray.DataArray] = (
            OrderedDict() if coords is None
            else OrderedDict({c.name:c for c in coords}))

        self._coord_edges: OrderedDict[Hashable, xarray.DataArray] = (
            OrderedDict() if coord_edges is None
            else OrderedDict({c.name:c for c in coord_edges}))

        # generate the coordinate centers based on the given edges
        for c_name in set(self._coord_edges.keys()) - set(self._coords.keys()):
            c_data = self._coord_edges[c_name]
            self._coords[c_name] = xarray.DataArray(
                data=(c_data.data[1:] + c_data.data[:-1]) / 2.0,
                name=c_name,
                dims=(c_name,),
                attrs=c_data.attrs)

        # generate the coordinate edges based on the given centers
        for c_name in set(self._coords.keys()) - set(self._coord_edges.keys()):
            # TODO skip in certain circumstances
            c_data = self._coords[c_name]
            a = (c_data.data[1:] + c_data.data[:-1])/2.0
            a = numpy.concatenate( (
                2*a[0:1]-a[1:2],
                a,
                2*a[-1:]-a[-2:-1] ))
            self._coord_edges[c_name] = xarray.DataArray(
                data=a,
                name=c_name,
                dims=(c_name,),
                attrs=c_data.attrs)

        # if not len(self._coords) and not len(self._coord_edges):
        #     # special case of no dimensions (e.g. globally binned)
        #     # TODO do error checking (make sure input data is dimensionless)
        #     pass

        # order of the dimensions names depends on the variables in data
        # check to make sure they are all consistent in their ordering
        # TODO

    @classmethod
    def merge(cls, other: Iterable['Data']) -> 'Data':
        """Merge data from 'other' into the dataset of experiments in 'self'."""
        itr = iter(other)
        merged = next(itr).copy()
        for i in itr:
            if not merged.equivalent(i):
                raise ValueError(
                    f'Cannot merge Data objects, they are not equivalent.')

            overlap_exp = set(i._data.keys()).intersection(
                set(merged._data.keys()))
            if overlap_exp != set():
                raise ValueError(
                    f'Cannot merge datasets, experiments "{overlap_exp}"'
                    ' already exist.')

            merged._data = OrderedDict({**merged._data, **i._data})
        return merged

    @property
    def dimensions(self) -> OrderedDict[Hashable, xarray.DataArray]:
        """The center of the binning dimension."""
        return self._coords

    @property
    def dimension_edges(self) -> OrderedDict[Hashable, xarray.DataArray]:
        """Return the edges of binning dimensions"""
        return self._coord_edges

    @property
    def datasets(self) -> OrderedDict[Hashable, xarray.Dataset]:
        """The data organized by experiment.

        The dict key is the experiment name, and the value is an xarray.Dataset
        containing all the variables."""
        return self._data

    @property
    def variables(self) -> Dict[Hashable, xarray.Dataset]:
        """The data organized by variable name.

        The dict key is the variable name, and the value is an xarray.Dataset
        containing each experiment.

        TODO: this is probably innefficient, need to use a view of the Dataset
        instead of creating a new one.
        """
        exp_names = self._data.keys()
        var_names = [v for v in next(iter(self._data.values())).data_vars]
        return {
            v: xarray.Dataset(data_vars=
                {e:self._data[e].data_vars[v] for e in exp_names}
                )
            for v in var_names}

    @property
    def nvars(self) -> int:
        return len(next(iter(self._data.values())).data_vars)

    def get_variables(self, variables: Union[Iterable[Hashable], Hashable] ) -> 'Data':
        if type(variables) is str:
            variables = set( (variables,) )
        else:
            variables = set(variables) # type: ignore

        all_vars = {str(k) for k in next(iter(self._data.values())).data_vars.keys()}
        if variables - all_vars != set():
            raise ValueError(f"variables do not exist {variables-all_vars}")

        drop_vars = all_vars - set(variables)
        ret = self.copy()
        for k in ret._data.keys():
            ret._data[k] = ret._data[k].drop_vars(drop_vars)
        return ret


    def copy(self) -> 'Data':
        """Make a deep copy of this class."""
        return copy.deepcopy(self)

    def equivalent(self, other: 'Data') -> bool:
        """Test if two Data objects are the same shape.

        They must have the same coordinates, and variables.
        """
        if type(other) is not Data:
            return False

        dims = self._coords.keys()
        if list(self._coords.keys()) != list(other._coords.keys()):
            return False

        return (
            all([self._coords[c].equals(other._coords[c]) for c in dims])
            and all([self._coord_edges[c].equals(other._coord_edges[c]) for c in dims])
            and self.variables.keys() == other.variables.keys()
        )

        # TODO, check the coordinates of the variables

    def remove_variable(self, variable_name: Hashable) -> None:
        """Remove the given variable name from all experiment data."""
        if variable_name not in self.variables.keys():
            raise ValueError(
                f'Variable {variable_name} was not found.')

        for exp in self._data:
            self._data[exp] = self._data[exp].drop_vars(variable_name)

    def diff(self, other: 'Data') -> 'Data':
        """Subtract one experiment from other experiments.

        Afterward, the 'self.diff_name' will be set."""
        if not self.equivalent(other):
            raise ValueError(
                'Cannot call diff() on non-equivalent datasets.')

        if self.diff_name is not None or other.diff_name is not None:
            raise ValueError(
                'Cannot call diff() on Data that is already a diff.')

        if len(other._data) != 1:
            # TODO allow diff() to work if number of exps is equal
            # between other and self?
            raise ValueError('Cannot call diff() with len(other.datasets) > 1')

        diff_data = self.copy()
        diff_data.diff_name = next(iter(other._data.keys()))
        for k in diff_data._data:
            diff_data._data[k] -= next(iter(other._data.values()))
        return diff_data
