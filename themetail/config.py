# -*- coding: utf-8 -*-

import os
import sys
import ConfigParser

import util


CONF_ENV_VARIABLE = 'THEMETAIL_CONF'


def get_config_path():
    path = os.getenv(CONF_ENV_VARIABLE)
    if path:
        return path
    return '~/.themetail.cnf'


def load():
    path = get_config_path()
    config = load_file(path)
    if config:
        if is_valid(config):
            return config

        util.logger.error('Aborting due to errors in themetail config')
        sys.exit(1)

    util.logger.error('No themetail configuration found at: %s' % path)
    sys.exit(1)


def load_file(filename):
    path = os.path.expanduser(filename)
    if not os.path.isfile(path):
        return None

    with open(path) as fp:
        return load_fp(fp)


def load_fp(fp):
    config = ConfigParser.SafeConfigParser({
        'auto-open-in-browser': False,
        'subdomain': None,
    })
    config.readfp(fp)
    return config


def has_configured(config, section, keys):
    for key in keys:
        if not config.has_option(section, key):
            msg = 'Missing config key "%s" in section "%s"'
            util.logger.error(msg, key, section)
            return False

        value = config.get(section, key)
        if not value:
            msg = 'Empty value for config key "%s" in section "%s"'
            util.logger.error(msg, key, section)
            return False
    return True


def is_valid(config):
    if not is_valid_client_section(config):
        return False
    return True


def is_valid_client_section(config):
    required = ['email', 'password']
    return has_configured(config, 'client', required)
