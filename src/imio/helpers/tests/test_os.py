# -*- coding: utf-8 -*-

from imio.helpers.testing import IntegrationTestCase

import os


class TestOsHelpersModule(IntegrationTestCase):
    """
    Test all helper methods of os_helpers module.
    """

    def test_get_tmp_folder(self):
        """
        """
        from imio.helpers.os_helpers import get_tmp_folder
        tmp_folder = get_tmp_folder()
        self.assertTrue(os.path.isdir(tmp_folder))
