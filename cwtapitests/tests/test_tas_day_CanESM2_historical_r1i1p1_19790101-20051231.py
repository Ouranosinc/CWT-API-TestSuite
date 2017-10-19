import os
import time
import sys
import unittest
import ConfigParser

from owslib.wps import WebProcessingService, ComplexDataInput

try:
    from cwtapitests.tests import wps_tests_utils
except ImportError:
    import wps_tests_utils


class TestWPS(unittest.TestCase):

    def setUp(self):
        self.config = ConfigParser.RawConfigParser()
        config_file_name = 'tas_day_CanESM2_historical_r1i1p1_19790101-20051231.cfg'
        if os.path.isfile(config_file_name):
            self.config.read(config_file_name)
        else:
            self.config.read('cwtapitests/tests/{0}'.format(config_file_name))

    def test_subset(self):
        config_dict = wps_tests_utils.config_is_available(
            'tas_day_CanESM2_historical_r1i1p1_19790101-20051231',
            ['process_name', 'file_location', 'file_wps_identifier',
             'file_is_complex', 'output_wps_identifier'],
            self.config, set_wps_host=True)

        wps = WebProcessingService(config_dict['wps_host'])
        if config_dict['file_is_complex']:
            file1 = ComplexDataInput(config_dict['file_location'])
        else:
            file1 = config_dict['file_location']
        # Here we set a dummy output to immediatly get the status file
        # and allow long process not to timeout, not sure about this...
        execution = wps.execute(
            config_dict['process_name'],
            inputs=[(config_dict['file_wps_identifier'], file1),
                    ('typename', 'testgeom:montreal_circles'),
                    ('featureids', 'montreal_circles.43')],
            output='output')

        # Wait for the process to finish, could get stuck here?
        while execution.getStatus() == 'ProcessAccepted':
            time.sleep(1)
            # Update status
            execution.checkStatus()
        if execution.getStatus() != 'ProcessSucceeded':
            raise RuntimeError()
        for process_output in execution.processOutputs:
            if process_output.identifier == \
               config_dict['output_wps_identifier']:
                break
        # Here the reference in process_output.reference is
        # left empty?!? Falling back to home made function
        exec_resp = wps_tests_utils.parse_execute_response(execution.response)
        out_file = exec_resp['outputs'][config_dict['output_wps_identifier']]
        
        # And now we would need to actually download and test something on this
        # out_file, which usually is a direct NetCDF file, but in the case of
        # multi output support is actually a json containing a list of files as
        # is the case in pavics subset_WFS. Requires another config
        self.assertEqual(out_file, something)

suite = unittest.TestLoader().loadTestsFromTestCase(TestWPS)

if __name__ == '__main__':
    run_result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(not run_result.wasSuccessful())
