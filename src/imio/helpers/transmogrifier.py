# -*- coding: utf-8 -*-
from copy import deepcopy

import os
import re


def correct_path(portal, path):
    """ Check if a path already exists on obj """
    original = path
    i = 1
    while portal.unrestrictedTraverse(path, default=None) is not None:  # path exists
        path = '{}-{:d}'.format(original, i)
        i += 1
    return path


def filter_keys(item, keys):
    """Return a copy of item with only given keys.

    :param item: yielded item (dict)
    :param keys: keys to keep
    :return: filtered item
    """
    if not keys:
        return deepcopy(item)
    new_item = {}
    for key in keys:
        new_item[key] = item[key]
    return new_item


def get_main_path(path='', subpath=''):
    """Return path/subpath if it exists. If path is empty, return buildout path."""
    if not path:
        # Are we in a classic buildout
        instance_home = os.getenv('INSTANCE_HOME')
        match = re.match('(.+)/parts/.+', instance_home)
        if match:
            path = match.group(1)
        else:
            path = os.getenv('PWD')
    if subpath:
        path = os.path.join(path, subpath)
    if os.path.exists(path):
        return path
    raise Exception("Path '{}' doesn't exist".format(path))


def pool_tuples(iterable, pool_len=2, e_msg=''):
    """Returns the iterable as tuples"""
    if not iterable:
        return iterable
    if len(iterable) % pool_len:
        raise Exception("{}: the given iterable must contain a multiple of {} elements: value = '{}'".format(
                        e_msg, pool_len, iterable))
    l_iter = iter(iterable)
    args = [l_iter for x in range(0, pool_len)]
    return zip(*args)


def relative_path(portal, fullpath):
    """Returns relative path following given portal (without leading slash).

    :param portal: leading object to remove from path
    :param fullpath: path to update
    :return: new path relative to portal object parameter
    """
    portal_path = '/'.join(portal.getPhysicalPath())  # not unicode, brain.getPath is also encoded
    if not fullpath.startswith(portal_path):
        return fullpath
    return fullpath[len(portal_path) + 1:]


def text_to_bool(item, key, log_method, log_params=None):
    """Changed to bool the text value of item[key].

    :param item: yielded item (usually dict)
    :param key: dict key
    :param log_method: special log method (as log_error in imio.transmogrifier.iadocs.utils)
    :param log_params: log method parameters
    :return: the boolean value
    """
    if log_params is None:
        log_params = {}
    if item[key] in (u'True', u'true'):
        return True
    elif item[key] in (u'False', u'false'):
        return False
    try:
        return bool(int(item[key] or 0))
    except Exception:  # noqa
        log_method(item, u"Cannot change '{}' key value '{}' to bool".format(key, item[key]), **log_params)
    return False
