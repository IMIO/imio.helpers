# -*- coding: utf-8 -*-
"""Fancy tree views."""
from plone import api
from plone.app.layout.navigation.navtree import buildFolderTree
from plone.app.layout.navigation.navtree import NavtreeStrategyBase
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

import json


class BaseRenderFancyTree(BrowserView):  # pylint: disable=R0921

    """Base view that displays a fancytree from a catalog query."""

    index = ViewPageTemplateFile('fancytree.pt')
    root = '/'  # must begin with slash

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.portal = api.portal.get()
        self.root_path = '/'.join(self.portal.getPhysicalPath()) + (self.root.lstrip('/') and self.root or '')

    def label(self):
        return self.context.Title()

    def __call__(self):
        if self.request.method == 'POST':
            uid = self.request.get('uid')
            self.request.response.redirect(self.redirect_url(uid))
            return ''

        return self.index()

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
        query = self.get_query()
        strategy = NavtreeStrategyBase()
        strategy.rootPath = self.root_path
        folder_tree = buildFolderTree(self.portal, None, query, strategy)
        return json.dumps(self.folder_tree_to_fancytree(folder_tree))

    def get_query(self):
        """Get the query."""
        raise NotImplementedError

    def redirect_url(self, uid):
        """Redirect url."""
        raise NotImplementedError
