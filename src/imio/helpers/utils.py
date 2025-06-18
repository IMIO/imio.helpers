# -*- coding: utf-8 -*-

from imio.helpers import _
from imio.helpers import HAS_PLONE_6_AND_MORE
from plone import api
from plone.namedfile.file import NamedBlobImage
from zope.interface import Invalid

import json


def create_image_content(
    container, title, id, data, filename=None, portal_type="Image"
):
    if HAS_PLONE_6_AND_MORE:
        obj = api.content.create(
            container=container,
            type=portal_type,
            id=id,
            title=title,
        )
        filename = filename or id
        obj.image = NamedBlobImage(**{"filename": filename, "data": data})
    else:
        obj = api.content.create(
            container=container,
            type=portal_type,
            id=id,
            title=title,
            file=data,
        )
    return obj


def is_valid_json(value):
    if value:
        try:
            json.loads(value)
        except:  # NOQA: E722
            raise Invalid(_(u"Invalid JSON."))
    return True
