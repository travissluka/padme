# (C) Copyright 2021-2022 UCAR
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

from abc import ABC, abstractmethod
import re
from typing import FrozenSet, MutableMapping, Type, List

from .data import Data


class DataHandler(ABC):

    _overrides = ['is_valid']

    def __init_subclass__(cls) -> None:
        # make sure subclasses explicitly override certain methods
        for o in cls._overrides:
            if o not in cls.__dict__:
                raise RuntimeError(
                    f'{cls} inherits from DataHandler but does not explicitly'
                    f' override the abstract method "{o}"')

    def __init__(self) -> None:
        self.first_use = True

    @abstractmethod
    def is_valid(self, data: Data) -> bool:
        return False

    @abstractmethod
    def process(self, data: Data, plot: 'PlotterBase') -> Data:
        self.first_use = False
        return data


class PlotterBase(ABC):
    _abstract = True
    _factory_name: str
    _overrides = ['is_valid']

    data_handlers: List[Type[DataHandler]] = []


    def __init_subclass__(cls, factory_name=None, abstract=False, **kwargs) -> None:
        """Method is called whenever a new PlotterBase subclass is defined."""

        # Set class properties.
        # The name used by the factory, if nothing is given, is a snake case
        # version of the class name.
        if factory_name is None:
            factory_name = (
                re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower())
        cls._factory_name = factory_name
        cls._abstract = abstract

        # make sure subclasses explicitly override the abstract methods
        for o in cls._overrides:
            if o not in cls.__dict__:
                raise RuntimeError(
                    f'{cls} inherits from PlotterBase but does not explicitly'
                    f' override the abstract method "{o}"')

        # Automatically register any subclasses.
        Plotter._register(cls)
        return super().__init_subclass__(**kwargs)  # type: ignore


    def __init__(self, data: Data):
        pass

    @classmethod
    def is_valid(cls, data: Data) -> bool:
        """Return True if this class (or any subclass) can plot the data."""
        return True


    @classmethod
    def get_valid_classes(cls, data: Data) -> List[Type['PlotterBase']]:
        """Get list of subclasses (including self) that can plot the data."""

        valid = []
        if cls.is_valid(data):
            # the current cls is a valid plot type for the given data. Get a
            # list of the valid subclasses
            for c in cls.__subclasses__():
                valid += c.get_valid_classes(data)

            # If there are no valid more-specific subclasses found, and this
            # class is not abstract, add this class to the list.
            if not len(valid) and not cls._abstract:
                valid += [cls, ]

        return valid


    def plot(self, data: Data, filename: str) -> None:
        """Generate a plot from the given data.

        This is the main method of the class, and the one method the user
        might call directly."""

        # Setup the plot before consuming any data
        self._pre_plot()

        # start consuming data
        data_handlers = [d() for d in self.data_handlers]
        while data.nvars:
            # find a valid data handler. If there are non, throw a warning.
            valid_data_handlers = [
                dh for dh in data_handlers if dh.is_valid(data)]
            if not len(valid_data_handlers):
                raise RuntimeWarning(
                    f'Unable to process anymore data when plotting with {self}'
                    f'\n\nData:\n{data}')
            data_handler = valid_data_handlers[0]

            # process the data. Make sure the data handler consumed something.
            remaining_data = data_handler.process(data, self)
            if remaining_data == data:
                raise RuntimeError(
                    f'Data handler {data_handler} did not consume any data'
                    f' for {self}')

        # all done consuming data. Finish the plot
        self._post_plot()
        self._save(filename)

        # TODO: return unconsumed data for another Plotter to consume?


    @abstractmethod
    def _pre_plot(self) -> None:
        """Setup anything that needs to be setup before plotting data."""
        pass

    @abstractmethod
    def _post_plot(self) -> None:
        """Called after all data has been plotted."""
        pass

    @abstractmethod
    def _save(self, filename: str) -> None:
        """Final call that saves plot to an output location."""
        pass


class __PlotterFactory():
    """TODO: insert descrtiption of __PlotterFactory"""
    _subclasses: MutableMapping[str, Type[PlotterBase]] = {}


    def __call__(self, data: Data) -> PlotterBase:
        """Instantiate a Plotter appropriate for the given data.

        The is_valid() method is called on available Plotters in the class
        hierarchy to determine which Plotter to use given the data passed."""

        # get all valid plotters that could be used
        plotters = PlotterBase.get_valid_classes(data)

        # TODO, if there are more than one valid class, how do we pick?
        # (shouldn't happen, for now.)
        if not len(plotters):
            raise RuntimeError(
                f'Cannot find a valid Plotter class for data: \n{data}')
        elif len(plotters) > 1:
            raise NotImplementedError(
                f'more than one valid plot type found {plotters}')

        return plotters[0](data)

    @property
    def types(self) -> FrozenSet[str]:
        """Get a list of the non-abstract registered Plotter classes."""
        return frozenset(
            [k for k,v in self._subclasses.items() if not v._abstract])

    def _register(self, cls: Type[PlotterBase]) -> None:
        if cls._factory_name in self._subclasses:
            raise RuntimeError(
                f'Cannot register Plotter class "{cls._factory_name}".'
                ' It has already been registered.')
        self._subclasses[cls._factory_name] = cls


Plotter = __PlotterFactory()
"""Plotter class factory"""