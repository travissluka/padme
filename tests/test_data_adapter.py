import pytest

from padme import DataAdapter

da_types=(
    'bespin',
    'ioda',
    'var_log')


@pytest.fixture(params=da_types)
def data_adapter(request):
    return request.param


def test_data_adapter_types():
    assert DataAdapter.types == set(da_types)


def test_data_adapter_init(data_adapter):
    pass

