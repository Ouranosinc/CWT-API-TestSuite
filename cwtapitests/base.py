import os
import requests
import unittest
from owslib.wps import WebProcessingService

class TestWPS(unittest.TestCase):
    wps_host = 'tbd'
    identifier = 'tbd'
    params = {}
    output_name = 'output'


    def setUp(self):
        """Run the WPS process and store the result."""
        self.wps = WebProcessingService(self.wps_host)

        # Get the description of the process
        self.p = self.wps.describeprocess(self.identifier)

        ### --------------------- ###
        ### Early fault detection ###
        ### --------------------- ###
        # Get the names of the inputs
        ins = [o.identifier for o in self.p.dataInputs]

        # Get the names of the outputs
        outs = [o.identifier for o in self.p.processOutputs]

        # Check that the params are in the inputs
        for key in self.params.keys():
            self.assertIn(key, ins)

        # Check that the desired output is defined
        self.assertIn(self.output_name, outs)
        ### --------------------- ###


        # Execute the process
        self.output = self.execute_wps()

    def execute_wps(self):
        """Execute the WPS process and return the output defined
        by self.output_name.

        Returns
        -------
        out : wps.Output
          Output object returned by the process.
        """

        inputs = []
        for key, val in self.params.items():
            if type(val) in [list, tuple]:
                for v in val:
                    inputs.append((key, v))
            else:
                inputs.append((key, val))


        # Here we set a dummy output to immediatly get the status file
        # and allow long process not to timeout, not sure about this...
        execution = self.wps.execute(self.identifier,
                                inputs=inputs,
                                output=self.output_name)

        # Wait for the process to finish, could get stuck here?
        while execution.getStatus() in ['ProcessAccepted', 'ProcessStarted']:
            # Update status
            execution.checkStatus(sleepSecs=1)

        if execution.getStatus() != 'ProcessSucceeded':
            raise RuntimeError()

        for out in execution.processOutputs:
            if out.identifier == self.output_name:
                return out

    def download(self, link, path='/tmp', strip=False):
        """Download the content of a link into a local file.

        Parameters
        ----------
        link : str
          URL
        path : str
          Local path to store file.
        strip : bool
          If True, store the file directly in path, otherwise keep
           relative directories within the link.

        Returns
        -------
        fn : str
          The path to the downloaded file.
        """
        import urllib3
        import errno

        u = urllib3.util.parse_url(link)
        p = u.path[1:]

        fn = os.path.join(path, os.path.basename(p) if strip else p)

        if not os.path.exists(os.path.dirname(fn)):
            try:
                os.makedirs(os.path.dirname(fn))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        req = requests.get(link, stream=True)
        with open(fn, 'wb') as f:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        return fn

    def fstrip(self, path):
        """Return a local file name."""
        if path.startswith('file://'):
            return path[6:]



