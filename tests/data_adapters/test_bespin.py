import pytest
import pathlib

import padme


FILES_ROOT=pathlib.PurePath(__file__).parent.parent / 'bespin_files'
files= [str(FILES_ROOT / f) for f in (
    'global.avhrr3_metop-a.nc',
    'global.sondes.nc',
    'lat.avhrr3_metop-a.nc',
    'latlon.avhrr3_metop-a.nc',
    'latlon.sondes.nc',
    'lat.sondes.nc')]


@pytest.fixture(params=files)
def filename(request):
    return request.param


def test_data_adapter_init(filename):
    da = padme.DataAdapter(adapter_name='bespin', filename=filename)
    # TODO do some meaningful error checking here