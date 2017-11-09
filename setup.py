import os
import glob
import unittest

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.md')).read()

reqs = ['owslib']

classifiers = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Science/Research',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX',
    'Programming Language :: Python',
    'Topic :: Scientific/Engineering :: Atmospheric Science']

def testsuite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('cwtapitests/tests',
                                      pattern='test_*.py')
    return test_suite

setup(name='cwtapitests',
      version='0.1',
      description='Tests for the ESGF CWT API.',
      long_description=README + '\n\n' + CHANGES,
      classifiers=classifiers,
      author='Blaise Gauvin St-Denis',
      author_email='gauvin-stdenis.blaise@ouranos.ca',
      url='https://github.com/Ouranosinc/CWT-API-TestSuite',
      license="http://www.apache.org/licenses/LICENSE-2.0",
      keywords='wps tests',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='setup.testsuite',
      install_requires=reqs,
      entry_points={'console_scripts': []},
      )
