# -*- coding: utf-8 -*-

import unittest

from themetail import client


class TestClient(unittest.TestCase):
    def test_url_generation(self):
        signin = client.url('/user/signin')
        self.assertEqual(signin, 'https://tictail.com/user/signin')

    def test_is_authenticated(self):
        client.session.cookies['tictail'] = 'foobar'
        self.assertTrue(client.is_authenticated())
        del client.session.cookies['tictail']
        self.assertFalse(client.is_authenticated())

    def test_setup_xsrf_token(self):
        del client.session.cookies['_xsrf']
        client.get_xsrf_token()
        self.assertTrue(client.has_cookie('_xsrf'))
        client.authenticate()
