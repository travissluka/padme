# (C) Copyright 2022-2022 UCAR
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

import pytest
import padme
import padme.core.plotter as plotter


@pytest.fixture
def empty_factory():
    # temporarily create and empty Plotter factory,
    # saving the existing classes in there to revert when this fixture is done.
    default_classes = padme.Plotter._subclasses
    padme.Plotter._subclasses = {}
    yield
    padme.Plotter._subclasses = default_classes


def test_plotter_register(empty_factory):
    # assert that a new empty factory was created
    assert padme.Plotter.types == set()

    # the following classes should fail to register for various reasons
    with pytest.raises(RuntimeError):
        # should fail because the required methods are missing
        class PlotterBad1(padme.PlotterBase):
            pass
    assert padme.Plotter.types == set()

    # the following classes should all register, abstract classes should
    # not show up in .types
    class PlotterGood(padme.PlotterBase):
        @classmethod
        def is_valid(cls, data: padme.Data) -> bool:
            return super().is_valid(data)
    class PlotterGood2(padme.PlotterBase, factory_name='foo'):
        @classmethod
        def is_valid(cls, data: padme.Data) -> bool:
            return super().is_valid(data)
    class PlotterGoodAbstract(padme.PlotterBase, abstract=True):
        @classmethod
        def is_valid(cls, data: padme.Data) -> bool:
            return super().is_valid(data)

    assert padme.Plotter.types == set(['plotter_good','foo'])

    # re-registering a class with a duplicate name should fail
    with pytest.raises(RuntimeError):
        class PlotterBad2(padme.PlotterBase, factory_name="foo"):
            def is_valid(cls, data: padme.Data) -> bool:
                return super().is_valid(data)


def test_plotter_types():

    # pick a class we know should be in the list
    assert len(list(padme.Plotter.types))
    cls = padme.plotters.two_dimensional.TwoDimensional._factory_name

    assert cls in padme.Plotter.types

    # abstract classes should not appear
    abstract_class = padme.plotters.matplotlib_base.MatplotlibBase._factory_name
    assert abstract_class not in padme.Plotter.types
