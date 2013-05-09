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
        return config

    print 'No themetail configuration found at: %s' % path
    sys.exit(1)


def has_configured(config, section, keys):
    for key in keys:
        if not config.has_option(section, key):
            return False

        value = config.get(section, key)
        if not value:
            return False
    return True


def is_valid_client_section(config):
    required = ['email', 'password']
    return has_configured(config, 'client', required)


def is_valid(config):
    if not is_valid_client_section(config):
        return False
    return True
