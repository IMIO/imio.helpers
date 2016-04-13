# -*- coding: utf-8 -*-
"""Test fancytree."""
import json

from plone import api

from imio.helpers.testing import IntegrationTestCase
from imio.helpers.fancytree.views import BaseRenderFancyTree


class RenderFancyTreeExample(BaseRenderFancyTree):

    """Fancy tree view with dummy get_query implementation for tests purpose."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_query(self):
        path = '/'.join(self.context.getPhysicalPath())
        return {
            'path': {'query': path, 'depth': -1},
            'portal_type': (
                'Folder',
                'Document',
                ),
        }


class TestBaseRenderFancyTree(IntegrationTestCase):

    """Test BaseRenderFancyTree view."""

    def test_get_data(self):
        """Test get_data method."""
        view = RenderFancyTreeExample(self.portal, self.portal.REQUEST)
        self.assertEqual(view.get_data(), '[]')

        # add some folders and documents
        myfolder = api.content.create(
            container=self.portal, type='Folder',
            id="myfolder", title="My folder")
        mydoc1 = api.content.create(
            container=myfolder, type='Document',
            id='mydoc1', title="My document")
        mydoc2 = api.content.create(
            container=myfolder, type='Document',
            id='mydoc2', title="My other document")

        output = view.get_data()
        expected = json.dumps([
            {
                'key': myfolder.UID(),
                'folder': True,
                'title': 'My folder',
                'children': [
                    {
                        'key': mydoc1.UID(),
                        'folder': False,
                        'title': 'My document',
                    },
                    {
                        'key': mydoc2.UID(),
                        'folder': False,
                        'title': 'My other document',
                    }
                ]
            }
            ])

        self.assertEqual(output, expected)
