# CWT-API-TestSuite

This package is meant to be an independent test suite for implementations of
the CWT API. It's architecture allows the same test logic to be applied to 
multiple implementations. What is being exercised are thus processes on live 
servers, not code within this repository. 

## Design notes

- This is currently a draft, to be converted into a full python package.
- Each test is associated with a particular file (or set of files). Ideally
  there would be a stable public server that hosts those files. 
- Given that there may be some variations in the the API (additional arguments),
  parameters can be configured for each library/process. 
- wps_tests_utils.py contains some old functions that are better handled by
  owslib, but there are still some cases where owslib does not seem to
  provide all the information required and these old functions do, need to
  investigate that...
