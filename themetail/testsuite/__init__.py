# -*- coding: utf-8 -*-
"""
"""

import os
import sys
import glob
import unittest


def get_modules():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    files = glob.glob(os.path.join(test_dir, 'test_*.py'))
    return [os.path.basename(name)[:-3] for name in files]


def main():
    modules = get_modules()
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    suite = unittest.defaultTestLoader.loadTestsFromNames(modules)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    exit_code = not (result.errors or result.failures)
    sys.exit(exit_code)
