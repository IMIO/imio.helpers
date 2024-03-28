# -*- coding: utf-8 -*-

from copy import deepcopy
from datetime import datetime
from imio.pyutils.utils import letters_sequence
from imio.pyutils.utils import safe_encode
from Products.CMFPlone.utils import safe_unicode
from six.moves import range
from six.moves import zip
from zope.tales.tales import CompilerError

import logging
import os
import re


logger = logging.getLogger('imio.helpers: transmogrifier')


def clean_value(value, isep=u'\n', strip=u' ', patterns=(), osep=None):
    """Clean unicode multiline value

    :param value: input string
    :param isep: input separator
    :param strip: chars to strip on each "line"
    :param patterns: tuple line patterns list to remove ("line" evaluation) (tuple = search, replace)
    :param osep: output separator
    :return: string
    """
    parts = []
    if not value:
        return value
    if osep is None:
        osep = isep
    for part in value.split(isep):
        part = part.strip(strip)
        for pattern, replace in patterns:
            part = re.sub(pattern, replace, part, flags=re.U)
        if part:
            parts.append(part)
    return osep.join(parts)


def filter_keys(item, keys, unfound=None):
    """Return a copy of item with only given keys.

    :param item: yielded item (dict)
    :param keys: keys to keep
    :param unfound: unfound value (default None)
    :return: filtered item
    """
    if not keys:
        return deepcopy(item)
    new_item = {}
    for key in keys:
        new_item[key] = item.get(key, unfound)
    return new_item


def get_correct_id(obj, oid, with_letter=False):
    """ Modify an id already existing in obj.

    :param obj: plone obj or dict or list
    :param oid: id to check
    :param with_letter: add a letter prefix
    :return: unique id
    """
    original = oid
    i = 1
    while oid in obj:
        sfx = with_letter and letters_sequence(i) or i
        oid = u'{}-{}'.format(original, sfx)
        i += 1
    return oid


def get_correct_path(portal, path):
    """ Check if a path already exists on obj """
    original = path
    i = 1
    while portal.unrestrictedTraverse(path, default=None) is not None:  # path exists
        path = '{}-{:d}'.format(original, i)
        i += 1
    return path


def get_obj_from_path(root, item={}, path_key='_path', path=None):
    """Gets object from path stored in item (dic) or from given path

    :param root: root object from where the search is done
    :param item: dict containing the path
    :param path_key: dict key to access the path value
    :param path: path value
    :return: the object or None if not found
    """
    if not path:
        path = item.get(path_key)
    if not path:
        return None
    path = safe_encode(path)
    if path.startswith('/'):
        path = path[1:]
    try:
        return root.unrestrictedTraverse(path)
    except (KeyError, AttributeError):
        return None


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
    """Returns the iterable as tuples

    :param iterable: a list or tuple
    :param pool_len: len of output pool tuples
    :param e_msg: prefix message when the iterable has not a correct len
    :return: an iterator giving pool tuples
    """
    if not iterable:
        return iterable
    if len(iterable) % pool_len:
        raise ValueError("{}: the given iterable must contain a multiple of {} elements: value = '{}'".format(
                         e_msg, pool_len, iterable))
    l_iter = iter(iterable)
    args = [l_iter for x in range(0, pool_len)]
    return list(zip(*args))


def relative_path(portal, fullpath, with_slash=True):
    """Returns relative path following given portal.

    :param portal: leading object to remove from path
    :param fullpath: path to update
    :param with_slash: keep leadind slash
    :return: new path relative to portal object parameter
    """
    portal_path = '/'.join(portal.getPhysicalPath())  # not unicode, brain.getPath is also encoded
    if not fullpath.startswith(portal_path):
        return fullpath
    shift = not with_slash and 1 or 0
    return fullpath[len(portal_path) + shift:]


def key_val(key, dic):
    """ Return a dic value or the key

    :param key: given key
    :param dic: dict
    :return: value or key
    """
    return dic.get(key, key)


def str_to_bool(item, key, log_method, **log_params):
    """Changed to bool the text value of item[key].

    :param item: yielded item (usually dict)
    :param key: dict key
    :param log_method: special log method (as log_error in imio.transmogrifier.iadocs.utils)
    :param log_params: log method keyword parameters
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


def split_text(text, length):
    """Split text on a word boundary at max length"""
    if text is None:
        return u'', u''
    part1 = text = safe_unicode(text)
    part2 = u''
    if len(text) > length:
        part1 = text[:length]
        part2 = text[length:]
        if part2[:1] != u' ':  # cut in a word
            s_i = part1.rfind(u' ')
            if s_i > length / 2:  # space after the middle of the part1
                part1 = part1[:s_i + 1]
                part2 = text[s_i + 1:]
    return part1, part2


def str_to_date(item, key, log_method, fmt='%Y/%m/%d', can_be_empty=True, as_date=True, min_val=None, max_val=None,
                **log_params):
    """Changed to date or datetime the text value of item[key]

    :param item: yielded item (usually dict)
    :param key: dict key
    :param log_method: special log method (as log_error in imio.transmogrifier.iadocs.utils)
    :param fmt: formatting date string
    :param can_be_empty: value can be empty or None
    :param as_date: return a date, otherwise a datetime
    :param min_val: minimal date
    :param max_val: maximum date
    :param log_params: log method keyword parameters
    :return: the date or datetime value
    """
    val = item.get(key)
    if not val and can_be_empty:
        return None
    try:
        dt = datetime.strptime(val, fmt)
        if as_date:
            dt = dt.date()
        if min_val and dt < min_val:
            # raise ValueError(u"Given date '{}' < minimal value '{}' => set to None".format(val, min_val))
            raise ValueError
        if max_val and dt > max_val:
            # raise ValueError(u"Given date '{}' > maximum value '{}' => set to None".format(val, max_val))
            raise ValueError
    except ValueError as ex:
        log_method(item, u"not a valid date '{}' in key '{}': {}".format(val, key, ex), **log_params)
        return None
    return dt


try:
    from collective.transmogrifier.utils import Expression as OrigExpression

    class Expression(OrigExpression):
        """Call the expression and log the expression"""

        def __init__(self, expression, transmogrifier, name, options, **extras):
            try:
                super(Expression, self).__init__(expression, transmogrifier, name, options, **extras)
            except CompilerError as e:
                logger.error("Error in part '{}', expression: '{}': {}".format(name, expression, e))
                raise e

        def __call__(self, item, **extras):
            try:
                return super(Expression, self).__call__(item, **extras)
            except Exception as e:
                logger.error("Error in part '{}', expression: '{}': {}".format(self.name, self.expression.text, e))
                raise e

    class Condition(Expression):
        """A transmogrifier condition expression with logging"""

        def __call__(self, item, **extras):
            return bool(super(Condition, self).__call__(item, **extras))

except ImportError:
    pass
