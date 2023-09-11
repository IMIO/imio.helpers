# -*- coding: utf-8 -*-

from imio.helpers.config import HAS_DASHBOARD
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IListContainedDexterityObjectsForDisplay(Interface):
    """Adapter interface that returns the dexterity objects contained
       in a dexterity Container in a state to be displayed."""


class IContainerOfUnindexedElementsMarker(Interface):
    """Marker interface to be used to mark a container that contains unindexed elements,
       so elements that are not indexed in the portal_catalog."""


if HAS_DASHBOARD:
    from collective.eeafaceted.collectionwidget.interfaces import ICollectiveEeafacetedCollectionwidgetLayer
    from collective.eeafaceted.dashboard.interfaces import IFacetedDashboardLayer

    class IIMIOHelpersLayer(ICollectiveEeafacetedCollectionwidgetLayer, IFacetedDashboardLayer):
        """Marker interface that defines a browser layer."""
else:
    class IIMIOHelpersLayer(IDefaultBrowserLayer):
        """Marker interface that defines a browser layer."""
