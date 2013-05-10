#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Themetail - Empowers local development of Tictail themes.

Usage:
    themetail preview [FILE] [--subdomain=<example>]
    themetail deploy [FILE] [--subdomain=<example>]
"""

import os
import sys
import logging
import webbrowser

from docopt import docopt

import client


def get_subdomain(arguments):
    subdomain = arguments['--subdomain']
    if subdomain:
        return subdomain

    subdomain = client.settings.get('client', 'subdomain')
    if not subdomain:
        logging.error('Aborting. No subdomain specified.')
        sys.exit(1)


def open_in_browser(url):
    auto_open = client.settings.get('client', 'auto-open-in-browser', False)
    if not auto_open:
        should_open = raw_input('Open in browser [Y/n]? ').strip().lower()
        if should_open != 'y':
            return False

    return webbrowser.open(url, new=2)


def push(arguments, preview=True):
    filename = arguments.get('FILE', None)
    if not filename:
        filename = os.path.join(os.getcwd(), 'build/theme.html')

    subdomain = get_subdomain(arguments)
    store = client.get_store(subdomain)
    if not store:
        msg = 'Aborting. Could not retrieve the store data.'
        logging.error(msg)
        sys.exit(1)

    if preview:
        msg = 'Going to save preview of theme %s for store "%s"'
    else:
        msg = 'Going to deploy theme %s for store "%s"'

    logging.info(msg, filename, subdomain)

    save = client.save_theme_from_file
    new_theme_id = save(store, filename, as_preview=preview)
    if not new_theme_id:
        return False

    if preview:
        updated_url = client.get_preview_url(subdomain, new_theme_id)
    else:
        updated_url = client.get_store_url(subdomain)

    if preview:
        logging.info('Awesomeness™. Preview updated!')
    else:
        logging.info('Epicness™. Deployed!')

    logging.info('Changes can be found at: %s', updated_url)
    open_in_browser(updated_url)


def preview(arguments):
    return push(arguments, preview=True)


def deploy(arguments):
    return push(arguments, preview=False)


def main(arguments):
    should_preview = arguments.get('preview', False)
    if should_preview:
        return preview(arguments)

    should_deploy = arguments.get('deploy', False)
    if should_deploy:
        return deploy(arguments)


if __name__ == '__main__':
    arguments = docopt(__doc__)
    main(arguments)
