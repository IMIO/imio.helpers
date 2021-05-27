# -*- coding: utf-8 -*-

from collective.fingerpointing.config import AUDIT_MESSAGE
from collective.fingerpointing.logger import log_info
from collective.fingerpointing.utils import get_request_information
from itertools import chain
from plone.api.validation import at_least_one_of
from plone.api.validation import mutually_exclusive_parameters
from random import choice
from random import sample
from random import seed
from time import time
from zope.component import getMultiAdapter

import logging
import os
import string


logger = logging.getLogger("imio.helpers")


def is_develop_environment():
    """
        Test if the environment variable named IS_DEV_ENV is added by the buildout and get the value
    """
    TRUISMS = ['yes', 'y', 'true', 'on']
    var = os.getenv('IS_DEV_ENV', 'false')

    if var.lower() in TRUISMS:
        logger.info('IS_DEV_ENV is deprecated, please use ENV variable.')
        return True
    elif get_environment() == 'dev':
        return True
    else:
        return False


def get_environment():
    """
        Get value of ENV environment variable.
        Value should be : dev, staging, preprod or prod.
    """
    env = os.getenv('ENV', 'prod')
    return env.lower()


def generate_password(length=10, digits=3, upper=2, lower=1, special=1, readable=True):
    """
        Create a random password with the specified length and minimum numbers
        of digit, upper and lower case letters, special characters.
    """
    seed(time())

    lowercase = string.lowercase.translate(None, "o")
    uppercase = string.uppercase.translate(None, "O")
    # string.punctuation contains !"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~
    specials = '!#$%&*+-<=>?@'
    # letters = "{0:s}{1:s}".format(lowercase, uppercase)
    letters = "{0:s}".format(lowercase)

    password = list(
        chain(
            (choice(uppercase) for _ in range(upper)),
            (choice(lowercase) for _ in range(lower)),
            (choice(letters) for _ in range((length - digits - upper - lower - special))),
            (choice(specials) for _ in range(special)),
            (choice(string.digits) for _ in range(digits)),
        )
    )
    if not readable:
        password = sample(password, len(password))
    return "".join(password)


def setup_logger(level=20):
    """
        When running "bin/instance run ...", the logger level is 30 (warn).
        It is possible to set it to 20 (info) or 10 (debug).
    """
    log = logging.getLogger()
    log.setLevel(level)
    for handler in logging.root.handlers:
        if handler.level == 30 and handler.formatter is not None:
            handler.level = level
            break


def fplog(action, extras):
    """collective.fingerpointing add log message."""
    user, ip = get_request_information()
    log_info(AUDIT_MESSAGE.format(user, ip, action, extras))


@mutually_exclusive_parameters('email', 'fullname')
@at_least_one_of('email', 'fullname')
def get_user_from_criteria(context, email=None, fullname=None):
    """
    :param context: context, with request as context.REQUEST
    :param email: part of user email
    :param fullname: part of user fullname
    :return: list of dict describing users
             [{'description': u'Bob Smith', 'title': u'Bob Smith', 'principal_type': 'user', 'userid': 'bsm',
               'email': 'bsm@mail.com', 'pluginid': 'mutable_properties', 'login': 'bsm', 'id': 'bsm'}]
    """
    hunter = getMultiAdapter((context, context.REQUEST), name='pas_search')
    criteria = {}
    if email:
        criteria['email'] = email
    if fullname:
        criteria['fullname'] = fullname
    return hunter.searchUsers(**criteria)
