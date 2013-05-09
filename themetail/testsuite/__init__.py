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
    config.SILENT = True

    envvar = config.CONF_ENV_VARIABLE
    backup = os.getenv(envvar)
    os.environ[envvar] = '~/.themetail_test.cnf'

    try:
        exit_code = run()
    except SystemExit:
        exit_code = 1

    if backup is None:
        os.unsetenv(envvar)
    else:
        os.environ[envvar] = backup

    sys.exit(exit_code)
