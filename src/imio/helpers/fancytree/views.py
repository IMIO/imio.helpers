# -*- coding: utf-8 -*-
"""Fancy tree views."""
import json

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.layout.navigation.navtree import buildFolderTree
from plone.app.layout.navigation.navtree import NavtreeStrategyBase


class BaseRenderFancyTree(BrowserView):  #pylint: disable=R0921

    """Base view that displays a fancytree from a catalog query."""

    index = ViewPageTemplateFile('fancytree.pt')

    def __call__(self):
        if self.request.method == 'POST':
            uid = self.request.get('uid')
            self.request.response.redirect(self.redirect_url(uid))
            return ''

        return self.index()

    def get_query(self):
        """Get the query."""
        raise NotImplementedError

    def folder_tree_to_fancytree(self, folder_tree):
        """Transform folder tree to a dict that will be used by fancy tree."""
        fancytree_data = []
        for child in folder_tree['children']:
            brain = child['item']
            if brain.portal_type == 'Folder' and not child['children']:
                # don't render empty folders
                continue

            item_info = {
                'title': brain.Title,
                'key': brain.UID,
                'folder': False,
            }

            if child['children']:
                item_info['folder'] = True
                item_info['children'] = self.folder_tree_to_fancytree(child)

            fancytree_data.append(item_info)

        return fancytree_data

    def get_data(self):
        """Get json data to render the fancy tree."""
        portal = api.portal.get()
        query = self.get_query()
        strategy = NavtreeStrategyBase()
        strategy.rootPath = '/'.join(portal.getPhysicalPath())
        folder_tree = buildFolderTree(portal, None, query, strategy)
        return json.dumps(self.folder_tree_to_fancytree(folder_tree))

    def redirect_url(self, uid):
        """Redirect url."""
        raise NotImplementedError
