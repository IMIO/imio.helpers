# -*- coding: utf-8 -*-

import os
import string
from itertools import chain
from time import time
from random import seed, choice, sample

from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager

from Products.CMFCore.tests.base.security import OmnipotentUser

from plone import api


def call_as_super_user(callable_obj, *args, **named_args):
    """
    Call a callable object after switching to a security manager with omnipotent user
    then fall back to the original security manager.
    """

    class SuperUser(OmnipotentUser):
        """
        OmnipotentUser does  not implement has_role() so we have to define our own super
        user class implmenting the method.
        """
        def has_role(self, *args, **kwargs):
            return True

    oldsm = getSecurityManager()
    # login as an super user
    portal = api.portal.getSite()
    newSecurityManager(None, SuperUser().__of__(portal.aq_inner.aq_parent.acl_users))
    try:
        result = callable_obj(*args, **named_args)
    except Exception, exc:
        # in case something wrong happen, make sure we fall back to original user
        setSecurityManager(oldsm)
        raise exc
    # fall back to original user
    setSecurityManager(oldsm)
    return result


def is_develop_environment():
    """
        Test if the environment variable named IS_DEV_ENV is added by the buildout and get the value
    """
    TRUISMS = ['yes', 'y', 'true', 'on']
    var = os.getenv('IS_DEV_ENV', 'false')
    if var.lower() in TRUISMS:
        return True
    else:
        return False


def generate_password(length=10, digits=1, upper=1, lower=1, special=1):
    """
        Create a random password with the specified length and minimum numbers of
        digit, upper and lower case letters, special characters.
    """
    seed(time())

    lowercase = string.lowercase.translate(None, "o")
    uppercase = string.uppercase.translate(None, "O")
    # string.punctuation contains !"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~
    specials = '!#$%&*+-<=>?@'
    letters = "{0:s}{1:s}{2:s}".format(lowercase, uppercase, specials)

    password = list(
        chain(
            (choice(uppercase) for _ in range(upper)),
            (choice(lowercase) for _ in range(lower)),
            (choice(string.digits) for _ in range(digits)),
            (choice(specials) for _ in range(special)),
            (choice(letters) for _ in range((length - digits - upper - lower - special)))
        )
    )
    return "".join(sample(password, len(password)))
