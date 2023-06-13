# (C) Copyright 2021-2022 UCAR
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

from typing import Callable, MutableMapping, FrozenSet, Any
import functools

from .data import Data


DataAdapterFunc = Callable[[Any], Data]


def register_data_adapter(name: str):
    """Register a data adapter.

    The data adapter can take in arbitrary arguments, but must return
    an xarray.Dataset with all the correctly formmated data.
    """
    def decorator(func: DataAdapterFunc) -> DataAdapterFunc:
        # register function with the factory
        func.factory_name = name  # type: ignore
        DataAdapter._register(func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Data:
            # use the specific data adapter to get the data
            data = func(*args, **kwargs)  # type: ignore

            # perform validity check on the data that was returned
            # TODO

            return data
        return wrapper
    return decorator


class __DataAdapterFactory():
    """Data adapter factory."""
    _adapters: MutableMapping[str, DataAdapterFunc] = {}

    def __call__(self, adapter_name: str, *args, **kwargs):
        """Create a new data adapter."""
        if adapter_name not in self._adapters:
            raise ValueError(
                f'Cannot create DataAdapter "{adapter_name}".'
                ' It has not been registered.')
        return self._adapters[adapter_name](*args, **kwargs) # type: ignore

    @property
    def types(self) -> FrozenSet[str]:
        """Get a list of the registered DataAdapter classes"""
        return frozenset(self._adapters.keys())

    def _register(self, func) -> None:
        if func.factory_name in self._adapters:
            raise RuntimeError(
                f'Cannot register DataAdapter "{func.factory_name}".'
                ' It has already been registered.')
        self._adapters[func.factory_name] = func


DataAdapter = __DataAdapterFactory()
"""Data adapter factory"""
