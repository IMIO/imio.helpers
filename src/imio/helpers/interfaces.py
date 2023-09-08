# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from collective.eeafaceted.collectionwidget.interfaces import ICollectiveEeafacetedCollectionwidgetLayer
from collective.eeafaceted.dashboard.interfaces import IFacetedDashboardLayer
from zope.interface import Interface


class IListContainedDexterityObjectsForDisplay(Interface):
    """Adapter interface that returns the dexterity objects contained
       in a dexterity Container in a state to be displayed."""


class IContainerOfUnindexedElementsMarker(Interface):
    """Marker interface to be used to mark a container that contains unindexed elements,
       so elements that are not indexed in the portal_catalog."""


class IIMIOHelpersLayer(ICollectiveEeafacetedCollectionwidgetLayer, IFacetedDashboardLayer):
    """Marker interface that defines a browser layer."""
