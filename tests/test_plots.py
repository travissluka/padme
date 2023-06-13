from select import select
import pytest
import pathlib

import padme

FILES_ROOT=pathlib.PurePath(__file__).parent / 'bespin_files'
files= [FILES_ROOT / f for f in (
    # 'global.avhrr3_metop-a.nc',
    # 'global.sondes.nc',
    # 'lat.avhrr3_metop-a.nc',
    #'latlon.avhrr3_metop-a.nc',
     #'latlon.sondes.nc',
    'lat.sondes.nc',
    )]


@pytest.fixture(params=files)
def filename(request):
    return request.param


def test_plot(filename):
    ofile = filename.stem + '.jpg'
    data = padme.DataAdapter(adapter_name='bespin', filename=str(filename)) #, select={'sensor_channel':3})
    plt = padme.Plotter(data)
    plt.plot(data, ofile)
    assert 1==2