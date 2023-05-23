# -*- coding: utf-8 -*-

from imio.helpers import HAS_PLONE_5_AND_MORE
from plone import api
from plone.namedfile.file import NamedBlobImage


def create_image_content(
    container, title, id, data, filename=None, portal_type="Image"
):
    if HAS_PLONE_5_AND_MORE:
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
