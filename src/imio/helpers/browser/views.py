# -*- coding: utf-8 -*-

from collective.eeafaceted.dashboard.browser.views import RenderTermPortletView
from imio.helpers.cache import _generate_modified_portal_type_volatile_name
from imio.helpers.cache import get_cachekey_volatile
from imio.helpers.cache import get_plone_groups_for_user
from imio.helpers.interfaces import IListContainedDexterityObjectsForDisplay
from imio.pyutils.utils import listify
from plone import api
from plone.app.caching.browser.controlpanel import RAMCache
from plone.app.querystring import queryparser
from plone.batching import Batch
from plone.dexterity.browser.view import DefaultView
from plone.memoize import ram
from Products.Five import BrowserView
from zope.component import getMultiAdapter


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


class IMIORenderTermView(RenderTermPortletView):

    def _get_portal_types(self):
        """By default, get the portal_type from the DashboardCollection query."""
        query = queryparser.parseFormquery(self.context, self.context.query)
        if not query.get('portal_type'):
            raise ram.DontCache
        return listify(query['portal_type']['query'])

    def number_of_items_cachekey(method, self, init=False):
        '''cachekey method for self.number_of_items.'''
        # cache until an obj of particular portal_type is modified
        # a DashboardCollection may rely on several portal_types
        dates = []
        for portal_type in self._get_portal_types():
            dates.append(
                get_cachekey_volatile(
                    _generate_modified_portal_type_volatile_name(
                        portal_type), method))
        # self.context is a DashboardCollection
        return (repr(self.context), get_plone_groups_for_user(), init) + tuple(dates)

    @ram.cache(number_of_items_cachekey)
    def number_of_items(self, init=False):
        """Just added caching until an item is modified results will remain the same."""
        return super(IMIORenderTermView, self).number_of_items(init=init)
