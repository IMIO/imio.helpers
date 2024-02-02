# -*- coding: utf-8 -*-

from imio.helpers.testing import IntegrationTestCase
from imio.helpers.tests.utils import require_module
from plone import api
from plone.app.textfield.value import RichTextValue


class TestAppyPod(IntegrationTestCase):

    @require_module('Products.Archetypes')
    def test_load_appy_pod_sample_archetypes(self):
        """Test for Archetypes."""
        docId = self.portal.invokeFactory('Document',
                                          id='doc',
                                          title='Original title')
        doc = getattr(self.portal, docId)
        view = doc.restrictedTraverse("@@appy_pod_sample")
        # does not break if called on an unexisting field or
        # not RichText field, just do nothing and display a portal_message
        view(field_name='title')
        self.assertEquals(doc.Title(), 'Original title')
        view(field_name='unexisting_field_name')
        # call it on a real RichText field_name
        self.assertEquals(doc.getText(), '')
        view(field_name='text')
        self.assertNotEquals(doc.getText(), '')

    def test_load_appy_pod_sample_dexterity(self):
        """Test for dexterity."""
        doc = api.content.create(container=self.portal,
                                 type='testingtype',
                                 id='testingtype',
                                 title='Original title')
        view = doc.restrictedTraverse("@@appy_pod_sample")
        # does not break if called on an unexisting field or
        # not RichText field, just do nothing and display a portal_message
        view(field_name='title')
        self.assertEquals(doc.Title(), 'Original title')
        view(field_name='unexisting_field_name')
        # call it on a real RichText field_name
        self.assertEquals(doc.text, None)
        view(field_name='text')
        self.assertTrue(isinstance(doc.text, RichTextValue))
