# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from imio.helpers.testing import IntegrationTestCase

from plone import api

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from zExceptions import Unauthorized


class TestSecurityModule(IntegrationTestCase):
    """
    Test all helper methods of security module.
    """

    def test_call_as_super_user(self):
        """
        """
        from imio.helpers.security import call_as_super_user

        # lower roles of ur test user
        setRoles(self.portal, TEST_USER_ID, ['Reader'])

        def some_unautorized_creation_method(obj_type, obj_id='some_id'):
            api.content.create(type=obj_type, id=obj_id, container=self.portal)

        # callable should throws Unauthorized exception
        exception_was_thrown = False
        try:
            some_unautorized_creation_method('Folder', obj_id='forbidden_folder')
        except Unauthorized:
            exception_was_thrown = True
        msg = 'callable throws no Unauthorized exception (and should be, for the sake of the test...)'
        self.assertTrue(exception_was_thrown, msg)
        # the folder should not be created
        self.assertTrue('forbidden_folder' not in self.portal.objectIds())

        # now try to call through call_with_super_user()
        try:
            call_as_super_user(
                some_unautorized_creation_method,
                'Folder',
                obj_id='forbidden_folder',
            )
        except Unauthorized:
            self.fail(msg='call_with_super_user throwed an Unauthorized exception')
        # the folder should be created
        self.assertTrue('forbidden_folder' in self.portal.objectIds())
