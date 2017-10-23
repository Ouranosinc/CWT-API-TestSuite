import os
import sys
import json
import unittest
import ConfigParser

from owslib.wps import WebProcessingService, ComplexDataInput

try:
    from cwtapitests.tests import wps_tests_utils
except ImportError:
    import wps_tests_utils

import netCDF4


class TestWPS(unittest.TestCase):

    def setUp(self):
        self.config = ConfigParser.RawConfigParser()
        config_file_name = 'MERRA2_100.statM_2d_slv_Nx.cfg'
        if os.path.isfile(config_file_name):
            self.config.read(config_file_name)
        else:
            self.config.read('cwtapitests/tests/{0}'.format(config_file_name))

    def test_spatial_subset_01(self):
        config_dict = wps_tests_utils.config_is_available(
            'subset',
            ['wps_host', 'process_name', 'file_location_198001',
             'file_wps_identifier', 'file_is_complex',
             'output_wps_identifier', 'wfs_typename_identifier',
             'wfs_featureid_identifier', 'wfs_typename', 'wfs_featureid'],
            self.config)

        wps = WebProcessingService(config_dict['wps_host'])
        if bool(int(config_dict['file_is_complex'])):
            file1 = ComplexDataInput(config_dict['file_location_198001'])
        else:
            file1 = config_dict['file_location_198001']
        # Here we set a dummy output to immediatly get the status file
        # and allow long process not to timeout, not sure about this...
        execution = wps.execute(
            config_dict['process_name'],
            inputs=[(config_dict['file_wps_identifier'], file1),
                    (config_dict['wfs_typename_identifier'],
                     config_dict['wfs_typename']),
                    (config_dict['wfs_featureid_identifier'],
                     config_dict['wfs_featureid']),
                    (config_dict['geoserver_identifier'],
                     config_dict['geoserver'])],
            output='output')

        # Wait for the process to finish, could get stuck here?
        while execution.getStatus() in ['ProcessAccepted', 'ProcessStarted']:
            # Update status
            execution.checkStatus(sleepSecs=1)
        if execution.getStatus() != 'ProcessSucceeded':
            raise RuntimeError()
        for process_output in execution.processOutputs:
            if process_output.identifier == \
               config_dict['output_wps_identifier']:
                break
        # Here the reference in process_output.reference is
        # left empty?!? Falling back to home made function
        exec_resp = wps_tests_utils.parse_execute_response(execution.response)

        json_response = json.loads(wps_tests_utils.get_wps_xlink(
            exec_resp['outputs'][config_dict['output_wps_identifier']]))
        out_file = os.path.basename(json_response[0])
        wps_tests_utils.get_wps_xlink(json_response[0], out_file)

        nc1 = netCDF4.Dataset(out_file, 'r')
        self.assertEqual(len(nc1.dimensions['lon']), 4)
        self.assertEqual(len(nc1.dimensions['lat']), 3)
        nc1.close()
        os.remove(out_file)

    def test_spatial_averager_01(self):
        config_dict = wps_tests_utils.config_is_available(
            'averager',
            ['wps_host', 'process_name', 'file_location_198001',
             'file_wps_identifier', 'file_is_complex',
             'output_wps_identifier', 'wfs_typename_identifier',
             'wfs_featureid_identifier', 'wfs_typename', 'wfs_featureid'],
            self.config)

        wps = WebProcessingService(config_dict['wps_host'])
        if bool(int(config_dict['file_is_complex'])):
            file1 = ComplexDataInput(config_dict['file_location_198001'])
        else:
            file1 = config_dict['file_location_198001']
        # Here we set a dummy output to immediatly get the status file
        # and allow long process not to timeout, not sure about this...
        execution = wps.execute(
            config_dict['process_name'],
            inputs=[(config_dict['file_wps_identifier'], file1),
                    (config_dict['wfs_typename_identifier'],
                     config_dict['wfs_typename']),
                    (config_dict['wfs_featureid_identifier'],
                     config_dict['wfs_featureid']),
                    (config_dict['geoserver_identifier'],
                     config_dict['geoserver'])],
            output='output')

        # Wait for the process to finish, could get stuck here?
        while execution.getStatus() in ['ProcessAccepted', 'ProcessStarted']:
            # Update status
            execution.checkStatus(sleepSecs=1)
        if execution.getStatus() != 'ProcessSucceeded':
            raise RuntimeError()
        for process_output in execution.processOutputs:
            if process_output.identifier == \
               config_dict['output_wps_identifier']:
                break
        # Here the reference in process_output.reference is
        # left empty?!? Falling back to home made function
        exec_resp = wps_tests_utils.parse_execute_response(execution.response)

        json_response = json.loads(wps_tests_utils.get_wps_xlink(
            exec_resp['outputs'][config_dict['output_wps_identifier']]))
        out_file = os.path.basename(json_response[0])
        wps_tests_utils.get_wps_xlink(json_response[0], out_file)

        nc1 = netCDF4.Dataset(out_file, 'r')
        self.assertEqual(len(nc1.dimensions['ocgis_geom_union']), 1)
        var1 = nc1.variables['T2MMIN']
        self.assertEqual(var1.dimensions, ('time', 'ocgis_geom_union'))
        nc1.close()
        os.remove(out_file)

    def test_ncmerge(self):
        config_dict = wps_tests_utils.config_is_available(
            'ncmerge',
            ['wps_host', 'process_name', 'file_location_198001',
             'file_location_198002', 'file_wps_identifier', 'file_is_complex',
             'output_wps_identifier'],
            self.config)

        wps = WebProcessingService(config_dict['wps_host'])
        if bool(int(config_dict['file_is_complex'])):
            file1 = ComplexDataInput(config_dict['file_location_198001'])
            file2 = ComplexDataInput(config_dict['file_location_198002'])
        else:
            file1 = config_dict['file_location_198001']
            file2 = config_dict['file_location_198002']
        # Here we set a dummy output to immediatly get the status file
        # and allow long process not to timeout, not sure about this...
        execution = wps.execute(
            config_dict['process_name'],
            inputs=[(config_dict['file_wps_identifier'], file1),
                    (config_dict['file_wps_identifier'], file2)],
            output='output')

        # Wait for the process to finish, could get stuck here?
        while execution.getStatus() in ['ProcessAccepted', 'ProcessStarted']:
            # Update status
            execution.checkStatus(sleepSecs=1)
        if execution.getStatus() != 'ProcessSucceeded':
            raise RuntimeError()
        for process_output in execution.processOutputs:
            if process_output.identifier == \
               config_dict['output_wps_identifier']:
                break
        # Here the reference in process_output.reference is
        # left empty?!? Falling back to home made function
        exec_resp = wps_tests_utils.parse_execute_response(execution.response)

        out_file = os.path.basename(
            exec_resp['outputs'][config_dict['output_wps_identifier']])
        wps_tests_utils.get_wps_xlink(
            exec_resp['outputs'][config_dict['output_wps_identifier']],
            out_file)

        nc1 = netCDF4.Dataset(out_file, 'r')
        self.assertEqual(len(nc1.dimensions['time']), 2)
        var1 = nc1.variables['T2MMIN']
        self.assertEqual(var1.dimensions, ('time', 'lat', 'lon'))
        nc1.close()
        os.remove(out_file)

suite = unittest.TestLoader().loadTestsFromTestCase(TestWPS)

if __name__ == '__main__':
    run_result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(not run_result.wasSuccessful())
