# -*- coding: utf-8 -*-
import os


def path_to_package(package, filepart=''):
    """Return the absolute path to p_filepart stored in p_package."""
    return os.path.join(
        os.path.dirname(package.__file__),
        filepart)
