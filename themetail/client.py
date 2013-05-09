# -*- coding: utf-8 -*-
"""
"""

import requests

from themetail import config

conf = config.get()
session = requests.Session()


def url(path):
    return 'https://tictail.com%s' % path


def get_credentials():
    email = conf.get('client', 'email')
    password = conf.get('client', 'password')
    return (email, password)


def has_cookie(name):
    return bool(session.cookies.get(name, False))


def is_authenticated():
    return has_cookie('tictail')


def authenticate():
    if is_authenticated():
        return True

    token = get_xsrf_token()
    email, password = get_credentials()
    data = dict(email=email, passwd=password, _xsrf=token, attempt=0)
    print data
    print session.cookies
    res = requests.post(url('/user/signin'), data=data)
    print res
    print res.cookies
    print dir(res)
    return True


def get_xsrf_token():
    if not has_cookie('_xsrf'):
        # A simple GET against /user/signin will set
        # the xsrf cookie in our requests session
        session.get(url('/user/signin'))
    return session.cookies['_xsrf']
