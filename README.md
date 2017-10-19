# CWT-API-TestSuite

Design notes

- This is currently a draft, to be converted into a full python package.

- Each test is associated with a particular file (or set of files). Ideally
  there is a stable public server that hosts those files, but it should
  always be possible to point to that same file on a different server through
  configuration (i.e. they are not hard-coded in the tests).

- Given that there are various WPS implementations in use
  (ESGF API, Birdhouse), further configuration parameters are required to
  specify the identifier of each input/output. Furthermore, some groups might
  have options in their WPS that others do not have, this can also be
  specified through configuration and skipped for implementations that do
  not support those options. This lack of uniformity might be unmanagable in
  the context of this test suite in the long run. There should really be just
  one climate data processing WPS API.

- wps_tests_utils.py contains some old functions that are better handled by
  owslib, but there are still some cases where owslib does not seem to
  provide all the information required and these old functions do, need to
  investigate that...
