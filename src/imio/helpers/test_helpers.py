# -*- coding: utf-8 -*-

from plone import api
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing.bbb import _createMemberarea
from plone.app.testing.helpers import setRoles
from plone.testing.z2 import Browser


class ImioTestHelpers():  # noqa
    """Helper class for tests.

    Assuming that self.layer, self.portal are defined in another class setUp...
    """

    def add_principal_to_groups(self, principal_id, group_ids):
        """We need to changeUser so getGroups is updated.

        :param principal_id: userid
        :param group_ids: group ids list
        """
        with api.env.adopt_roles(['Manager']):
            for group_id in group_ids:
                self.portal.portal_groups.addPrincipalToGroup(principal_id, group_id)
            self.change_user(self.member.getId())

    def change_user(self, username):
        """Logs out currently logged user and logs in p_loginName."""
        logout()
        if username == 'admin':
            login(self.layer['app'], username)
        else:
            login(self.portal, username)
        self.member = api.user.get_current()  # noqa
        self.portal.REQUEST['AUTHENTICATED_USER'] = self.member

    def create_user(self, username, pwd='humpf', roles=('Member', ), groups=(), mb_area=False):
        """Creates a user named p_username with some p_roles.

        :param username: username
        :param pwd: password
        :param roles: roles
        :param groups: groups
        :param mb_area: bool to create member area
        :return: new user
        """
        with api.env.adopt_roles(['Manager']):
            new_user = api.user.create(
                email='test@test.be',
                username=username,
                password=pwd,
                roles=[],
                properties={})
            setRoles(self.portal, username, roles)
            for group in groups:
                self.add_principal_to_groups(username, group)
            if mb_area:
                _createMemberarea(self.portal, username)
            return new_user

    def remove_principal_from_groups(self, principal_id, group_ids):
        """We need to changeUser so getGroups is updated.

        :param principal_id: userid
        :param group_ids: group ids list
        """
        with api.env.adopt_roles(['Manager']):
            for group_id in group_ids:
                self.portal.portal_groups.removePrincipalFromGroup(principal_id, group_id)
            self.change_user(self.member.getId())


class BrowserTest(ImioTestHelpers):
    """
    Helper class for Browser tests.
    """

    def setUp(self):
        super(BrowserTest, self).setUp()
        self.browser = Browser(self.portal)
        self.browser.handleErrors = False

    def browser_login(self, user, password):
        login(self.portal, user)
        self.browser.open(self.portal.absolute_url() + '/logout')
        self.browser.open(self.portal.absolute_url() + "/login_form")
        self.browser.getControl(name='__ac_name').value = user
        self.browser.getControl(name='__ac_password').value = password
        self.browser.getControl(name='submit').click()
