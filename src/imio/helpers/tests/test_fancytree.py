# -*- coding: utf-8 -*-
"""Test fancytree."""
from imio.helpers.fancytree.views import BaseRenderFancyTree
from imio.helpers.testing import IntegrationTestCase
from plone import api

import json


class RenderFancyTreeExample(BaseRenderFancyTree):

    """Fancy tree view with dummy get_query implementation for tests purpose."""

    def index(self):
        return "index"

    def get_query(self):
        return {
            'path': {'query': self.root_path, 'depth': -1},
            'portal_type': (
                'Folder',
                'Document',
            ),
        }

    def redirect_url(self, uid):
        return uid


class TestBaseRenderFancyTree(IntegrationTestCase):

    """Test BaseRenderFancyTree view."""

    def test_label(self):
        view = BaseRenderFancyTree(self.portal, self.request)
        self.assertEqual(view.label(), 'Plone site')

    def test_redirect_url(self):
        view = BaseRenderFancyTree(self.portal, self.request)
        with self.assertRaises(NotImplementedError):
            view.redirect_url('some_uid')

    def test_get_query(self):
        view = BaseRenderFancyTree(self.portal, self.request)
        with self.assertRaises(NotImplementedError):
            view.get_query()

    def test_call(self):
        view = RenderFancyTreeExample(self.portal, self.request)
        self.assertEqual(view(), "index")

        request = self.request
        request.method = 'POST'
        request['uid'] = 'myuid'
        self.assertEqual(view(), '')
        self.assertEqual(view.request.response.headers['location'], 'myuid')

    def test_get_data(self):
        """Test get_data method."""
        view = RenderFancyTreeExample(self.portal, self.request)
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
        expected = sorted(json.loads(expected))
        output = sorted(json.loads(output))
        self.assertEqual(output, expected)
