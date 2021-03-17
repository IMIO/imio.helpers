# -*- coding: utf-8 -*-

from cgi import escape
from zope.i18nmessageid import MessageFactory
from ZPublisher.Converters import type_converters

import json


_ = MessageFactory('imio.helpers')


# create type converter for :json
if 'field2json' not in type_converters:
    def field2json(v):
        try:
            v = json.loads(v)
        except ValueError:
            raise ValueError("Invalid json " + escape(repr(v)))
        return v
    type_converters['json'] = field2json
