# -*- coding: utf-8 -*-

from Acquisition import aq_inner
from imio.helpers import HAS_PLONE_4
from imio.helpers.interfaces import IListContainedDexterityObjectsForDisplay
from plone import api
from plone.app.caching.browser.controlpanel import RAMCache
from plone.batching import Batch
from plone.dexterity.browser.view import DefaultView
from Products.Five import BrowserView
from zope.component import getMultiAdapter


if HAS_PLONE_4:
    from plone.app.content.browser.foldercontents import FolderContentsBrowserView
    from plone.app.content.browser.foldercontents import FolderContentsTable
    from plone.app.content.browser.foldercontents import FolderContentsView
else:
    FolderContentsBrowserView = object
    FolderContentsTable = object
    FolderContentsView = object


class ContainerView(DefaultView):
    """ """

    collapse_all_fields = False
    collapse_all_fields_onload = False
    fields_to_collapse = []  # not yet used
    fields_to_collapse_onload = []  # not yet used


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


class IMIORAMCache(RAMCache):
    """ """

    def update(self):
        super(IMIORAMCache, self).update()
        self.stats = self.ramCache.getStatistics()


class IMIOFolderContentsTable(FolderContentsTable):
    """Overrided so @@folder_contents work on a DashboardCollection."""

    def contentsMethod(self):
        context = aq_inner(self.context)

        # use DashboardCollection.brains_results if available
        contentsMethod = None
        if hasattr(context.__class__, 'brains_results'):
            contentsMethod = context.brains_results
        return contentsMethod or super(IMIOFolderContentsTable, self).contentsMethod()


class IMIOFolderContentsBrowserView(FolderContentsBrowserView):
    table = IMIOFolderContentsTable


class IMIOFolderContentsView(FolderContentsView):

    def contents_table(self):
        # override to use IMIOFolderContentsTable instead FolderContentsTable
        table = IMIOFolderContentsTable(aq_inner(self.context), self.request)
        return table.render()
