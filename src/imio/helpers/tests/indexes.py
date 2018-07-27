# -*- coding: utf-8 -*-
#
# File: indexes.py
#
# Copyright (c) 2013 by Imio.be
#
# GNU General Public License (GPL)
#

from OFS.interfaces import IItem
from plone.indexer import indexer


@indexer(IItem)
def reversedUID(obj):
    """
      Return UID reversed...
    """
    return obj.UID()[::-1]
