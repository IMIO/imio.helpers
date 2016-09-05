# -*- coding: utf-8 -*-
from zope.component import getMultiAdapter

from Products.Five import BrowserView

from plone import api
from plone.batching import Batch

from imio.helpers.interfaces import IListContainedDexterityObjectsForDisplay


class ContainerFolderListingView(BrowserView):
    """
      This manage the elements listed on the view of a dexterity container
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        self.portal = portal_state.portal()

    def listRenderedContainedElements(self, portal_types=(), widgets_to_render=(), b_size=30, b_start=0):
        """
          Get the contained elements, rendered for display.
          If p_portal_types is specified, only return elements having the required portal_type.
          If p_widgets_to_render is specified, only render given fields/widgets.
        """
        result = IListContainedDexterityObjectsForDisplay(self.context).listContainedObjects(portal_types,
                                                                                             widgets_to_render,
                                                                                             b_start=b_start,
                                                                                             b_size=b_size)
        batch = Batch(result, b_size, b_start, orphan=1)
        return batch

    def author(self, author_id):
        """
          Return fullname of given p_author_id
        """
        membership = api.portal.get_tool('portal_membership')
        memberInfos = membership.getMemberInfo(author_id)
        return memberInfos and memberInfos['fullname'] or author_id

    def authorname(self):
        author = self.author()
        return author and author['fullname'] or self.creator()

    def update_table(self):
        return self.context.restrictedTraverse('@@imio-folder-listing-table').index()
