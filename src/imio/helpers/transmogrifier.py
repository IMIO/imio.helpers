# -*- coding: utf-8 -*-

import os
import re


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
