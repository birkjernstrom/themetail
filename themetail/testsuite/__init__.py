# -*- coding: utf-8 -*-
"""
"""

import os
import sys
import glob
import unittest

from themetail import config


def get_modules():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    files = glob.glob(os.path.join(test_dir, 'test_*.py'))
    return [os.path.basename(name)[:-3] for name in files]


def run():
    modules = get_modules()
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    suite = unittest.defaultTestLoader.loadTestsFromNames(modules)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    exit_code = not (result.errors or result.failures)
    return exit_code


def main():
    envvar = config.CONF_ENV_VARIABLE
    backup = os.getenv(envvar)
    os.putenv(envvar, '~/.themetail_test.cnf')

    try:
        exit_code = run()
    except (Exception, SystemExit):
        exit_code = 1

    if backup is not None:
        os.putenv(envvar, backup)
    else:
        os.unsetenv(envvar)

    sys.exit(exit_code)
