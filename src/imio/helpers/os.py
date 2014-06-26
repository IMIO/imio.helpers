# -*- coding: utf-8 -*-

import os


def get_os_tmp_folder():
    tmp = '/tmp'
    if os.path.exists(tmp) and os.path.isdir(tmp):
        res = tmp
    elif 'TMP' in os.environ:
        res = os.environ['TMP']
    elif 'TEMP' in os.environ:
        res = os.environ['TEMP']
    else:
        raise "Sorry, I can't find a temp folder on your machine."
    return res
