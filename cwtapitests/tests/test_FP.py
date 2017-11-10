import unittest
import json
import netCDF4 as nc
from flyingpigeon.tests.common import TESTDATA
from owslib.wps import ComplexDataInput
from cwtapitests import TestWPS
import unittest

class TestMerge(TestWPS):
    identifier = 'ncmerge'
    params = {'resource': '__from_config__'}
    output_name = 'output'

    def resource(self, value):
        return map(ComplexDataInput, value.split(','))

    def test(self):
        """Confirm that the length of the output file along the time
        dimension is the sum of the length of the input files.
        """

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
    identifier = 'subset'
    params = {'resource':'__from_config__',
              'typename':'region_admin_poly',
              'featureids':'region_admin_poly.16',
              'geoserver':'__from_config__'}
    output_name = 'output'

    def resource(self, value):
        return map(ComplexDataInput, value.split(','))

    def test(self):
        # The result is actually a json file containing a list of NetCDF links
        fn = self.download(self.output, path='/tmp')
        # Downloading again, the actual NetCDF outputs this time
        with open(fn, 'r') as f:
            fn = self.download(json.loads(f.read())[0], path='/tmp')
        with nc.Dataset(fn) as D:
            self.assertEqual(len(D.dimensions['lon']), 4)
            self.assertEqual(len(D.dimensions['lat']), 3)


