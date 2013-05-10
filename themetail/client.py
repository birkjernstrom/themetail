# -*- coding: utf-8 -*-

import os
import json

import requests

import util
import config

settings = config.load()
session = requests.Session()


def url(path):
    return 'https://tictail.com%s' % path


def get_credentials():
    email = settings.get('client', 'email')
    password = settings.get('client', 'password')
    return (email, password)


def has_cookie(name):
    return bool(session.cookies.get(name, False))


def is_authenticated():
    return has_cookie('tictail')


def signin():
    if is_authenticated():
        return True

    token = get_xsrf_token()
    email, password = get_credentials()
    data = dict(email=email, passwd=password, _xsrf=token, attempt=0)
    response = session.post(url('/user/signin'), data=data)
    success = response.status_code == 200
    return (success and is_authenticated())


def signout():
    session.cookies = {}


def get_xsrf_token():
    if not has_cookie('_xsrf'):
        # A simple GET against /user/signin will set
        # the xsrf cookie in our requests session
        session.get(url('/user/signin'))
    return session.cookies['_xsrf']


def jsonrpc_encode(method, params):
    data = dict(jsonrpc='2.0', method=method, params=params, id=None)
    return json.dumps(data)


def jsonrpc_post(payload):
    data = dict(jsonrpc=payload, _xsrf=get_xsrf_token())
    response = session.post(url('/apiv2/rpc/v1/'), data=data)
    if response.status_code == 200:
        return response.json()['result']
    return {}


def get_store(subdomain):
    signin()
    theme_edit_url = url('/dashboard/store/%s/themes/edit' % subdomain)
    response = session.get(theme_edit_url)
    if response.status_code != 200:
        return None

    # Begin hack
    body = response.text
    needle = 'ClientSession = {'
    json_index_start = body.rindex(needle) + len(needle) - 1
    json_index_end = body.index('};', json_index_start) + 1
    data = body[json_index_start:json_index_end].strip()
    data = json.loads(data)
    # End hack

    return data['storekeeper']['stores'][subdomain]


def get_store_url(subdomain):
    return 'http://%s.tictail.com' % subdomain


def get_preview_url(subdomain, theme_id):
    path = '/dashboard/store/%s/themes/preview/%s' % (subdomain, theme_id)
    return url(path)


def save_theme_from_file(store, theme_file, as_preview=True):
    if not os.path.isfile(theme_file):
        util.logger.error('Aborting. Could not find theme build file.')
        return False

    if not os.access(theme_file, os.R_OK):
        util.logger.error('Aborting. Cannot read the theme build file.')
        return False

    with open(theme_file, 'r') as build:
        content = build.read().strip()
        return save_theme(store, content, as_preview=as_preview)


def save_theme(store, theme, as_preview=True):
    signin()
    hook = 'before_preview' if as_preview else 'before_deploy'
    if not util.execute_hook(hook):
        util.logger.info('Instructed to abort by the %s hook.', hook)
        return False

    if as_preview:
        res = generate_preview_request(store, theme)
    else:
        res = generate_deploy_request(store, theme)

    new_theme_id = res.get('id', False)
    if not new_theme_id:
        return False

    hook = 'after_preview' if as_preview else 'after_deploy'
    util.execute_hook(hook, new_theme_id)
    return new_theme_id


def generate_preview_request(store, theme):
    theme_id = store['store_theme_id']
    return jsonrpc_post(jsonrpc_encode('theme.update', {
        'theme_id': theme_id,
        'content': theme,
        'is_preview': True,
    }))


def generate_deploy_request(store, theme):
    store_id = store['id']
    return jsonrpc_post(jsonrpc_encode('store.theme.update', {
        'store_id': store_id,
        'content': theme,
        'is_preview': False,
    }))
