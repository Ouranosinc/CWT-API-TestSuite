import os
import time
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
        config_file_name = 'tas_day_MPI-ESM-MR_historical_r1i1p1.cfg'
        if os.path.isfile(config_file_name):
            self.config.read(config_file_name)
        else:
            self.config.read('cwtapitests/tests/{0}'.format(config_file_name))

    def test_temporal_subset(self):
        config_dict = wps_tests_utils.config_is_available(
            'tas_day_MPI-ESM-MR_historical_r1i1p1',
            ['wps_host', 'process_name', 'file_location',
             'file_wps_identifier', 'file_is_complex',
             'output_wps_identifier'],
            self.config)

        wps = WebProcessingService(config_dict['wps_host'])
        if bool(int(config_dict['file_is_complex'])):
            file1 = ComplexDataInput(config_dict['file_location'])
        else:
            file1 = config_dict['file_location']
        # Here we set a dummy output to immediatly get the status file
        # and allow long process not to timeout, not sure about this...
        execution = wps.execute(
            config_dict['process_name'],
            inputs=[(config_dict['file_wps_identifier'], file1),
                    ('initial_datetime', '2001-02-01T00:00:00'),
                    ('final_datetime', '2001-04-01T00:00:00')],
            output='output')

        # Wait for the process to finish, could get stuck here?
        while execution.getStatus() == 'ProcessAccepted':
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

        nc1 = netCDF4.Dataset(out_file,'r')
        self.assertEqual(len(nc1.dimensions['time']), 60)
        nc1.close()
        os.remove(out_file)

suite = unittest.TestLoader().loadTestsFromTestCase(TestWPS)

if __name__ == '__main__':
    run_result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(not run_result.wasSuccessful())
