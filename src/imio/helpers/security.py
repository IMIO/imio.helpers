# -*- coding: utf-8 -*-

from itertools import chain
from random import choice
from random import sample
from random import seed
from time import time

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
