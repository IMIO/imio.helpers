# -*- coding: utf-8 -*-

import os


def get_file_data(filename):
    file_path = os.path.join(os.path.dirname(__file__), filename)
    fd = open(file_path, "rb")
    data = fd.read()
    fd.close()
    return data


def restricted_method(self, *args, **kwargs):
    print("%s : Archetype is required for this test" % self.__name__)
    # raise Exception(f"{module_name} is not installed, can't access this method.")


def require_module(module_name):
    try:
        __import__(module_name)
        return lambda func: func
    except ImportError:
        return restricted_method


def unrequire_module(module_name):
    try:
        __import__(module_name)
        return restricted_method
    except ImportError:
        return lambda func: func
