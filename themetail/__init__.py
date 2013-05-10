#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Themetail - Empowers local development of Tictail themes.

An unofficial Tictail command-line tool for automatically synchronizing
local copies of themes to your Tictail store. Along with some added flair
to enable developers and designers to work in their preferred environment
along with their favourite gadgets.

Usage:
    themetail list-themes
    themetail clone <theme> [<directory>]
    themetail watch [FILE] [DIR] [--subdomain=<example>]
    themetail preview [FILE] [DIR] [--subdomain=<example>]
    themetail deploy [FILE] [DIR] [--subdomain=<example>]
"""

import os
import sys
import time
import webbrowser
import subprocess

from docopt import docopt
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

import util
import client

__author__ = 'Birk Nilson <birk@tictail.com>'
__license__ = 'MIT'
__version__ = '0.8.0'
__all__ = [
    'util', 'client',
    'list-themes', 'clone', 'watch', 'deploy', 'preview',
    'push', 'open_in_browser', 'get_subdomain', 'Watcher',
    'ensure_valid_watch_directory', 'ensure_valid_watch_file',
]


class Watcher(FileSystemEventHandler):
    def __init__(self, observer, arguments, directory, theme_filename):
        super(Watcher, self).__init__()
        self.observer = observer
        self.arguments = arguments
        self.directory = directory
        self.theme_filename = theme_filename
        self.has_opened_browser = False

    def is_theme_event(self, event):
        path = os.path.join(self.directory, self.theme_filename)
        return event.src_path == path

    def moved_within_directory(self, event):
        return event.dest_path.startswith(self.directory)

    def sync(self):
        browser_default = not self.has_opened_browser
        try:
            was_pushed = push(self.arguments,
                              self.theme_filename,
                              preview=True,
                              browser_default=browser_default,
                              browser_prompt=False)
        except SystemExit:
            self.observer.stop()
            return

        if was_pushed:
            self.has_opened_browser = True

    def on_created(self, event):
        pass

    def on_modified(self, event):
        if self.is_theme_event(event):
            self.sync()

    def on_deleted(self, event):
        if self.is_theme_event(event):
            util.logger.error('Deleted the theme file')
            self.observer.stop()

    def on_moved(self, event):
        if self.is_theme_event(event):
            util.logger.error('Moving the theme file is not supported')
            self.observer.stop()

        if not self.moved_within_directory(event):
            return


def ensure_valid_watch_file(filename):
    if not filename.endswith('.html'):
        util.logger.error('The main theme file does not end in .html')
        sys.exit(1)

    if not os.access(filename, os.R_OK):
        util.logger.error('Cannot read the main theme file')
        sys.exit(1)


def ensure_valid_watch_directory(directory):
    theme_path = os.path.join(directory, 'theme.html')
    ensure_valid_watch_file(theme_path)


def get_subdomain(arguments):
    subdomain = arguments['--subdomain']
    if subdomain:
        return subdomain

    subdomain = client.settings.get('client', 'subdomain')
    if not subdomain:
        util.logger.error('Aborting. No subdomain specified.')
        sys.exit(1)


def get_directory(arguments):
    directory = arguments['DIR']
    if directory:
        return directory
    return os.getcwd()


def open_in_browser(url, prompt_fallback=True, default=False):
    auto_open = client.settings.get('client', 'auto-open-in-browser', default)
    if not auto_open:
        if not prompt_fallback:
            return False

        should_open = raw_input('Open in browser [Y/n]? ').strip().lower()
        if should_open != 'y':
            return False

    return webbrowser.open(url, new=2)


def push(arguments,
         filename,
         preview=True,
         browser_default=False,
         browser_prompt=True):
    subdomain = get_subdomain(arguments)
    store = client.get_store(subdomain)
    if not store:
        msg = 'Aborting. Could not retrieve the store data.'
        util.logger.error(msg)
        sys.exit(1)

    if preview:
        msg = 'Going to save preview of theme %s for store "%s"'
    else:
        msg = 'Going to deploy theme %s for store "%s"'

    util.logger.info(msg, filename, subdomain)

    save = client.save_theme_from_file
    new_theme_id = save(store, filename, as_preview=preview)
    if not new_theme_id:
        return False

    if preview:
        updated_url = client.get_preview_url(subdomain, new_theme_id)
    else:
        updated_url = client.get_store_url(subdomain)

    if preview:
        util.logger.info('Awesomeness™. Preview updated!')
    else:
        util.logger.info('Epicness™. Deployed!')

    util.logger.info('Changes can be found at: %s', updated_url)
    open_in_browser(updated_url,
                    prompt_fallback=browser_prompt,
                    default=browser_default)


def preview(arguments, filename):
    return push(arguments, filename, preview=True)


def deploy(arguments, filename):
    return push(arguments, filename, preview=False)


def watch(arguments):
    path = get_directory(arguments)
    filename = arguments['FILE']
    if filename:
        path = os.path.dirname(os.path.join(path, filename))
        filename = os.path.split(filename)[-1]
        ensure_valid_watch_directory(path)
    else:
        filename = 'theme.html'
        ensure_valid_watch_directory(path)

    observer = Observer()
    event_handler = Watcher(observer, arguments, path, filename)
    observer.schedule(event_handler, path=path, recursive=True)
    observer.start()

    try:
        while observer.should_keep_running():
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def clone(arguments):
    theme = arguments['<theme>']
    choices = util.get_theme_bundle()
    if theme not in choices:
        msg = 'Given theme %s does not exist. The choices are:'
        util.logger.error(msg, theme)
        list_themes(arguments)
        sys.exit(1)

    directory = arguments['<directory>']
    if not directory:
        directory = theme

    theme_path = os.path.join(util.get_theme_bundle_path(), theme)
    theme_path = '%s/*' % theme_path

    if subprocess.call(['mkdir', '-p', directory]):
        msg = 'Could not create theme directory %s'
        util.logger.error(msg, directory)
        sys.exit(1)

    if subprocess.call(['cp', theme_path, directory]):
        msg = 'Could not copy theme content to directory %s'
        util.logger.error(msg, directory)
        sys.exit(1)


def list_themes(arguments):
    for theme in util.get_theme_bundle():
        print theme


def main(arguments):
    should_list_themes = arguments.get('list-themes', False)
    if should_list_themes:
        return list_themes(arguments)

    should_clone = arguments.get('clone', False)
    if should_clone:
        return clone(arguments)

    should_watch = arguments.get('watch', False)
    if should_watch:
        return watch(arguments)

    filename = arguments['FILE']
    if not filename:
        directory = get_directory(arguments)
        filename = os.path.join(directory, 'build/theme.html')

    should_preview = arguments.get('preview', False)
    if should_preview:
        return preview(arguments, filename)

    should_deploy = arguments.get('deploy', False)
    if should_deploy:
        return deploy(arguments, filename)


if __name__ == '__main__':
    arguments = docopt(__doc__)
    main(arguments)
