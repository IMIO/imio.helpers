# -*- coding: utf-8 -*-
import os


def path_to_package(package, filepart=""):
    """Return the absolute path to p_filepart stored in p_package."""
    return os.path.join(os.path.dirname(package.__file__), filepart)


def is_test_url():
    """Return True if the current URL is a test URL, False otherwise."""
    url = os.getenv("PUBLIC_URL", "")
    return ".imio-test.be" in url or ".imio-acceptation.be" in url
