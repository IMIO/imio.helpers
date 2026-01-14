# -*- coding: utf-8 -*-

from imio.helpers import ws
from imio.helpers.testing import FunctionalTestCase
from requests.exceptions import MissingSchema


class TestWS(FunctionalTestCase):
    def test_get_auth_token(self):
        """For now just call the function and check that it is MissingSchema."""
        self.assertRaises(MissingSchema, ws.get_auth_token)

    def test_send_json_request(self):
        """For now just call the function and check that it is MissingSchema."""
        self.assertRaises(MissingSchema, ws.send_json_request, '')
