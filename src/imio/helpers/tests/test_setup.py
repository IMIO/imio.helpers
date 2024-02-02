# -*- coding: utf-8 -*-
from imio.helpers.setup import load_type_from_package
from imio.helpers.setup import load_workflow_from_package
from imio.helpers.setup import load_xml_tool_only_from_package
from imio.helpers.setup import remove_gs_step
from imio.helpers.testing import IntegrationTestCase
from plone import api

import unittest


class TestSetupModule(IntegrationTestCase):
    """
    Test all helper methods of setup module.
    """

    def setUp(self):
        self.portal = self.layer['portal']

    def test_load_type_from_package(self):
        types_tool = api.portal.get_tool('portal_types')
        portal_type = types_tool.get('Discussion Item')
        self.assertTrue(portal_type.filter_content_types)
        portal_type.filter_content_types = False
        self.assertFalse(portal_type.filter_content_types)
        self.assertTrue(load_type_from_package(
            'Discussion Item', 'profile-Products.CMFPlone:plone'))
        portal_type = types_tool.get('Discussion Item')
        self.assertTrue(portal_type.filter_content_types)
        # not found portal_type
        self.assertFalse(load_type_from_package(
            'Folder2', 'profile-Products.CMFPlone:plone'))
        # not found profile_id
        self.assertFalse(load_type_from_package(
            'Folder', 'profile-Products.CMFPlone:plone2'))
        # type not managed by given profile_id
        self.assertFalse(load_type_from_package(
            'testingtype', 'profile-Products.CMFPlone:plone'))
        # reimport a Dexterity fti
        self.assertTrue(load_type_from_package(
            'testingtype', 'profile-imio.helpers:testing'))
        # with purge_actions=True
        self.assertTrue(load_type_from_package(
            'testingtype', 'profile-imio.helpers:testing', purge_actions=True))

    def test_load_workflow_from_package(self):
        wkf_tool = api.portal.get_tool('portal_workflow')
        wkf_obj = wkf_tool.get('intranet_workflow')
        states = wkf_obj.states
        self.assertIn('internal', states)
        states.deleteStates(['internal'])
        self.assertNotIn('internal', states)
        self.assertTrue(load_workflow_from_package(
            'intranet_workflow', 'profile-Products.CMFPlone:plone'))
        wkf_obj = wkf_tool.get('intranet_workflow')
        states = wkf_obj.states
        self.assertIn('internal', states)
        # not found WF
        self.assertFalse(load_workflow_from_package(
            'intranet_workflow2', 'profile-Products.CMFPlone:plone'))
        # not found profile_id
        self.assertFalse(load_workflow_from_package(
            'intranet_workflow', 'profile-Products.CMFPlone:plone2'))
        # WF not managed by given profile_id
        self.assertFalse(load_workflow_from_package(
            'comment_review_workflow', 'profile-Products.CMFPlone:plone'))

    @unittest.skip('Not working')
    def test_load_xml_tool_only_from_package(self):
        wkf_tool = api.portal.get_tool('portal_workflow')
        wkf_obj = wkf_tool.get('intranet_workflow')
        states = wkf_obj.states
        self.assertIn('internal', states)
        self.assertTupleEqual(wkf_tool.getChainForPortalType('Image'), ())
        self.assertTupleEqual(wkf_tool.getChainForPortalType('Document'), ('intranet_workflow',))
        # some changes
        states.deleteStates(['internal'])
        self.assertNotIn('internal', states)
        wkf_tool.setChainForPortalTypes(('Image',), ('one_state_workflow',))
        wkf_tool.setChainForPortalTypes(('Document',), ('one_state_workflow',))
        self.assertTupleEqual(wkf_tool.getChainForPortalType('Image'), ('one_state_workflow',))
        self.assertTupleEqual(wkf_tool.getChainForPortalType('Document'), ('one_state_workflow',))
        # we reload default config
        self.assertTrue(load_xml_tool_only_from_package('portal_workflow', 'profile-Products.CMFPlone:plone'))
        self.assertTupleEqual(wkf_tool.getChainForPortalType('Image'), ())  # chain is reset
        self.assertTupleEqual(wkf_tool.getChainForPortalType('Document'), ('one_state_workflow',))  # not in xml
        wkf_obj = wkf_tool.get('intranet_workflow')
        states = wkf_obj.states
        self.assertNotIn('internal', states)  # be sure it's not recursive
        # not found tool
        self.assertFalse(load_xml_tool_only_from_package('portal_workflow2', 'profile-Products.CMFPlone:plone'))
        # not found profile_id
        self.assertFalse(load_xml_tool_only_from_package('portal_workflow', 'profile-Products.CMFPlone:plone2'))

    def test_remove_gs_step(self):
        ps_tool = api.portal.get_tool('portal_setup')
        step_id = u'mockmailhost-various'
        self.assertIn(step_id, ps_tool.getSortedImportSteps())
        self.assertTrue(remove_gs_step(step_id))
        self.assertNotIn(step_id, ps_tool.getSortedImportSteps())
