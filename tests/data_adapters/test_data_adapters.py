import pytest

import padme

da_types=(
    'bespin',
    'ioda',
    'var_log')


@pytest.fixture(params=da_types)
def data_adapter_name(request):
    return request.param


def test_data_adapter_types():
    assert padme.DataAdapter.types == set(da_types)
