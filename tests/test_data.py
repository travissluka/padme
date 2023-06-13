import numpy
import padme
import pytest
import xarray

edges = {
    'lat' : xarray.DataArray(
        **{k:'latitude' for k in ('name','dims')},
        data=numpy.linspace(-90.0, 90.0, 7),
        attrs={
            'units': 'degrees_north',
            }),

    'lon' : xarray.DataArray(
        **{k:'longitude' for k in ('name','dims')},
        data=numpy.linspace(0.0, 360.0, 13),
        attrs={'units': 'degrees_east'}),
}

centers = {
    'lat' : xarray.DataArray(
        **{k:'latitude' for k in ('name','dims')},
        data=numpy.linspace(-75.0, 75.0, 6),
        attrs={'units': 'degrees_north'}),

    'lon' : xarray.DataArray(
        **{k:'longitude' for k in ('name','dims')},
        data=numpy.linspace(15.0, 345.0, 12),
        attrs={'units': 'degrees_east'}),
}

dim_map = {
    '1D': ('lat',),
    '2D': ('lat', 'lon'),
    }

@pytest.fixture(params=dim_map.keys())
def dims(request):
    return request.param

@pytest.fixture
def coord_edges(dims):
    return list(edges[d] for d in dim_map[dims])

@pytest.fixture
def coord_centers(dims):
    return list(centers[d] for d in dim_map[dims])

@pytest.fixture
def raw_data(dims):
    dim_lens = [len(centers[d]) for d in dim_map[dims] ]
    return xarray.Dataset(
        data_vars={
            k: (
                (centers[d].name for d in dim_map[dims]),
                numpy.random.rand(*dim_lens)) for k in ('var1','var2')
        }
    )

@pytest.fixture
def data(coord_edges, raw_data):
    return padme.Data('exp1', data=raw_data, coord_edges=coord_edges)

#-------------------------------------------------------------------------------

def test_data_coords(coord_edges, coord_centers):

    # all the following should fail
    with pytest.raises(ValueError):
        # must define either dimension and/or dimension_edge
        padme.Data('exp1', data=xarray.Dataset())

    # create using only coordinate edges, test that the generated centers are
    # correct
    d = padme.Data('exp1', data=xarray.Dataset(), coord_edges=coord_edges)
    assert len(d.dimensions) == len(coord_edges)
    assert len(d.dimension_edges) == len(coord_edges)
    for c in coord_edges:
        assert c.name in d.dimension_edges
        assert c.equals(d.dimension_edges[c.name])
    for c in coord_centers:
        assert c.name in d.dimensions
        assert c.equals(d.dimensions[c.name])

    # create using only coordinate centers, test that the generated edges are
    # correct
    d = padme.Data('exp1', data=xarray.Dataset(), coords=coord_centers)
    assert len(d.dimensions) == len(coord_edges)
    assert len(d.dimension_edges) == len(coord_edges)
    for c in coord_edges:
        assert c.name in d.dimension_edges
        assert c.equals(d.dimension_edges[c.name])
    for c in coord_centers:
        assert c.name in d.dimensions
        assert c.equals(d.dimensions[c.name])

def test_data_data(data: padme.Data):
    assert 'var1' in data.datasets['exp1']

def test_data_vars(data):
    assert data.variables.keys() == set( ('var1','var2') )

    data.remove_variable('var1')
    assert data.variables.keys() == set( ('var2',) )

    with pytest.raises(ValueError):
        data.remove_variable('foo')


def test_data_copy(data: padme.Data):
    data2 = data.copy()
    assert data.equivalent(data2)
    assert data._data['exp1'].data_vars['var1'].equals(
        data2._data['exp1'].data_vars['var1'])

    data._data['exp1'] *= 2
    assert not data._data['exp1'].data_vars['var1'].equals(
        data2._data['exp1'].data_vars['var1'])


def test_data_equivalent(data: padme.Data):
    assert not data.equivalent('foo') # type: ignore

    d2 = data.copy()
    d2._data['exp2'] = d2._data.pop('exp1')
    assert data.equivalent(d2)

    d2._coords['lat2'] = d2._coords['latitude']
    assert not data.equivalent(d2)

    d3 = data.copy()
    d3._data['exp1'] = d3._data['exp1'].rename({'var1': 'var7'})
    assert not data.equivalent(d3)


def test_data_merge(data: padme.Data):
    d2 = data.copy()
    with pytest.raises(ValueError):
        padme.Data.merge( (data,d2) )

    d2._data['exp2'] = d2._data.pop('exp1')
    d2 = padme.Data.merge( (data, d2) )

    d2 = data.copy()
    d2._data['exp2'] = d2._data.pop('exp1').rename({'var1':'var7'})
    with pytest.raises(ValueError):
        padme.Data.merge( (data, d2) )


def test_data_diff(data: padme.Data):
    d2 = data.copy()
    d2._data['exp2'] = d2._data.pop('exp1')*3

    # diff that should work
    diff = d2.diff(data)
    xarray.testing.assert_allclose(
        diff._data['exp2'], data._data['exp1']*2)
    assert data.diff_name is None
    assert diff.diff_name == 'exp1'

    # cant do diff with a diffd object
    with pytest.raises(ValueError):
        diff.diff(data)

    # can't diff non-equivalent objects
    d3 = d2.copy()
    d3._data['exp2'] = d3._data['exp2'].rename({'var1':'var7'})
    with pytest.raises(ValueError):
        data.diff(d3)

    # cant diff if 'other' has more than 1 exp
    d4 = d2.copy()
    d4._data['exp3'] = d4._data['exp2']
    with pytest.raises(ValueError):
        data.diff(d4)

