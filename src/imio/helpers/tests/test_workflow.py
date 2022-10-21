# -*- coding: utf-8 -*-
from imio.helpers.testing import IntegrationTestCase
from imio.helpers.workflow import do_transitions
from imio.helpers.workflow import get_state_infos
from imio.helpers.workflow import get_transitions
from imio.helpers.workflow import remove_state_transitions
from plone import api


class TestWorkflowModule(IntegrationTestCase):
    """
    Test all helper methods of workflow module.
    """

    def setUp(self):
        self.portal = self.layer['portal']

    def test_do_transitions(self):
        obj = api.content.create(container=self.portal.folder, id='mydoc', type='Document')
        self.assertEqual(api.content.get_state(obj), 'internal')
        # apply one transition
        do_transitions(obj, 'submit')
        self.assertEqual(api.content.get_state(obj), 'pending')
        # apply multiple transitions
        do_transitions(obj, ['publish_internally', 'publish_externally'])
        self.assertEqual(api.content.get_state(obj), 'external')
        do_transitions(obj, ['submit', 'retract', 'hide'])
        self.assertEqual(api.content.get_state(obj), 'private')

    def test_get_state_infos(self):
        self.portal.portal_workflow.setChainForPortalTypes(('Document', ), ('intranet_workflow', ))
        obj = api.content.create(container=self.portal.folder, id='mydoc', title='My document', type='Document')
        self.assertDictEqual(get_state_infos(obj), {'state_title': u'Internal draft', 'state_name': 'internal'})
        do_transitions(obj, 'submit')
        self.assertDictEqual(get_state_infos(obj), {'state_title': u'Pending review', 'state_name': 'pending'})

    def test_get_transitions(self):
        obj = api.content.create(container=self.portal.folder, id='mydoc', type='Document')
        self.assertEqual(get_transitions(obj),
                         ['publish_internally', 'hide', 'submit'])
        do_transitions(obj, 'submit')
        self.assertEqual(get_transitions(obj),
                         ['publish_internally', 'retract', 'publish_externally', 'reject'])
        do_transitions(obj, 'publish_externally')
        self.assertEqual(get_transitions(obj), ['retract'])

    def test_remove_state_transitions(self):
        wf_tool = api.portal.get_tool('portal_workflow')
        wf = wf_tool['intranet_workflow']
        self.assertFalse(remove_state_transitions('intranet_workflow', 'unknown_state'))
        self.assertTupleEqual(wf.states['internal'].transitions, ('hide', 'publish_internally', 'submit'))
        self.assertFalse(remove_state_transitions('intranet_workflow', 'internal'))  # nothing removed
        self.assertTrue(remove_state_transitions('intranet_workflow', 'internal', ['hide', 'submit']))  # removed
        self.assertTupleEqual(wf.states['internal'].transitions, ('publish_internally',))
        # add duplicates to simulate bad manipulation
        wf.states['internal'].transitions = tuple(['publish_internally', 'submit', 'submit'])
        self.assertTupleEqual(wf.states['internal'].transitions, ('publish_internally', 'submit', 'submit'))
        self.assertTrue(remove_state_transitions('intranet_workflow', 'internal'))
        self.assertTupleEqual(wf.states['internal'].transitions, ('publish_internally', 'submit'))
