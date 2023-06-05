# -*- coding: utf-8 -*-

from AccessControl.SecurityManagement import getSecurityManager
from App.config import getConfiguration
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
from zope.globalrequest import getRequest

import inspect
import logging
import os
import string
import Zope2


logger = logging.getLogger("imio.helpers")


def is_develop_environment():
    """
        Test if the environment variable named ENV is added by the buildout and get the value
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


def get_zope_root():
    """Get zope root from nowhere.
    Can be useful in IProcessStarting subscriber...
    """
    db = Zope2.DB
    connection = db.open()
    return connection.root().get('Application', None)


def set_site_from_package_config(product_name, zope_app=None):
    """Set site context from plone-path given a product-config zope config.
    Can be used in an IProcessStarting subscriber...

    <product-config XXX>
        plone-path YYY
    </product-config>

    :param product_name: configured product name string
    :param zope_app: zope application (to avoid to open a second connection if not necessary)
    :return: portal object if defined or None
    """
    config = getattr(getConfiguration(), 'product_config', {})
    package_config = config.get(product_name)
    if package_config and package_config.get('plone-path'):  # can be set on instance1 only or not at all
        if not zope_app:
            zope_app = get_zope_root()
        try:
            site = zope_app.unrestrictedTraverse(package_config['plone-path'])
        except KeyError:  # site not found
            return None
        try:
            from zope.app.component.hooks import setSite
        except ImportError:
            from zope.component.hooks import setSite
        setSite(site)
        return site
    return None


def counted_logger(logger_name=''):
    """ """
    caller = inspect.stack()[1][3]
    logger = logging.getLogger("{0} ({1})".format(
        logger_name, inspect.stack()[1][3]))
    request = getRequest()
    req_key = "counter_logger__{0}".format(caller.replace(' ', ''))
    counter = request.get(req_key, 0) + 1
    request.set(req_key, counter)
    logger.info("Counter {0}".format(counter))
    return logger


def check_zope_admin():
    """
        Check if current user is the Zope admin.
    """
    user = getSecurityManager().getUser()
    if user.has_role("Manager") and user.__module__ in (
        "Products.PluggableAuthService.PropertiedUser",
        "AccessControl.users",
        "AccessControl.User",
    ):
        return True
    return False
