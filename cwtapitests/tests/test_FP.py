import netCDF4 as nc
from flyingpigeon.tests.common import TESTDATA
from owslib.wps import ComplexDataInput
from cwtapitests import TestWPS

host = 'http://localhost:8093/wps'


class TestMerge(TestWPS):
    wps_host = host
    identifier = 'ncmerge'
    params = {'resource': [ComplexDataInput(TESTDATA['cmip5_tasmax_2006_nc']),
                         ComplexDataInput(TESTDATA['cmip5_tasmax_2006_nc'])]}
    output_name = 'output'

    def test(self):
        # Count the total length of the time dimension of the input files.
        n = 0
        for res in self.params['resource']:
            with nc.Dataset(self.fstrip(res.value)) as D:
                n += len(D.dimensions['time'])

        fn = self.download(self.output.reference, path='/tmp')

        with nc.Dataset(fn) as D:
            self.assertIn('tasmax', D.variables)

            # Check that the time dimension has the length of the sum of the
            # source files.
            self.assertEqual(len(D.dimensions['time']), n)


class TestSpatialSubset(TestWPS):
    wps_host = host
    identifier = 'subset'
    params = {'resource':'path_to_MERRA2_100.statM_2d_slv_Nx.198001.nc',
              'typename':'region_admin_poly',
              'featureids':'region_admin_poly.16',
              'geoserver':'http://localhost:8087/geoserver/wfs'}
    output_name = 'output'

    def test(self):
        fn = self.download(self.output.reference, path='/tmp')
        with nc.Dataset(fn) as D:
            self.assertEqual(len(D.dimensions['lon']), 4)
            self.assertEqual(len(D.dimensions['lat']), 3)

