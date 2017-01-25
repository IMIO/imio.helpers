# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.interface import Interface


class IListContainedDexterityObjectsForDisplay(Interface):
    """Adapter interface that returns the dexterity objects contained
       in a dexterity Container in a state to be displayed."""
