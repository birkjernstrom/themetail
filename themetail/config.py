# -*- coding: utf-8 -*-
"""
"""

import os
import sys
import ConfigParser

CONF_ENV_VARIABLE = 'THEMETAIL_CONF'


def get_config_path():
    path = os.getenv(CONF_ENV_VARIABLE)
    if path:
        return path

    return os.path.expanduser('~/.themetail.cnf')


def load(path):
    path = get_config_path()
    if not os.path.isfile(path):
        return None

    with open(path) as fp:
        return load_fp(fp)


def load_fp(fp):
    config = ConfigParser.SafeConfigParser()
    config.readfp(fp)
    return config


def get():
    path = get_config_path()
    config = load(path)
    if config:
        if is_valid(config):
            return config

        print 'Aborting due to errors in themetail config'
        sys.exit(1)

    print 'No themetail configuration found at: %s' % path
    sys.exit(1)


def has_configured(config, section, keys, log=False):
    def log(message, *args):
        if log:
            print message % args

    for key in keys:
        if not config.has_option(section, key):
            msg = 'ERROR (Config): Missing key "%s" in section "%s"'
            log(msg, key, section)
            return False

        value = config.get(section, key)
        if not value:
            msg = 'ERROR (Config): Empty value for key "%s" in section "%s"'
            log(msg, key, section)
            return False
    return True


def is_valid_client_section(config, log=False):
    required = ['email', 'password']
    return has_configured(config, 'client', required, log=log)


def is_valid(config, log=False):
    if not is_valid_client_section(config, log=log):
        return False
    return True
