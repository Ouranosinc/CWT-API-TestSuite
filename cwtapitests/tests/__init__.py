import unittest
from cwtapitests import conf, TestWPS
import test_FP

def all_subclasses(cls):
    return cls.__subclasses__() + [g for s in cls.__subclasses__()
                                   for g in all_subclasses(s)]

def load_suite(host):
    """Create a test suite, including copies of each test for all hosts.

    Parameters
    ----------
    host : str, list
      List of host where tests should be run. If `all`, run of all hosts
      listed in the configuration file.
    """

    klasses = all_subclasses(TestWPS)
    names = [k.identifier for k in klasses]

    if host == 'all':
        hosts = conf.keys()
        hosts.remove('default')
        hosts.remove('DEFAULT')
    else:
        hosts = host.split(',')

    suite = unittest.TestSuite()
    for name in hosts:
        keys = conf[name].keys()
        if 'include' in keys and 'exclude' in keys:
            raise ValueError("config file error.")

        includes = conf[name].get('include', '*')
        excludes = conf[name].get('exclude', '')

        includes = names if includes == '*' else includes.split(',')
        excludes = names if excludes == '*' else excludes.split(',')

        set(includes).discard(set(excludes))

        for k in klasses:
            kid = k.identifier
            if kid in includes:
                suite.addTest(
                    TestWPS.parametrize(k, hostname=name)
                )
    return suite


