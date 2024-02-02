# -*- coding: utf-8 -*-

from ZPublisher.Converters import type_converters

import json


try:
    from cgi import escape  # Python 2.x
except ImportError:
    from html import escape


# create type converter for :json
if 'json' not in type_converters:
    def field2json(v):
        try:
            v = json.loads(v)
        except ValueError:
            raise ValueError("Invalid json " + escape(repr(v)))
        return v
    type_converters['json'] = field2json
