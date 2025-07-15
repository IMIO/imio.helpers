# -*- coding: utf-8 -*-
from plone import api


def uninstall_product(context):
    if context.readDataFile("imio.helpers_uninstall.txt") is None:
        return

    setup_tool = api.portal.get_tool("portal_setup")
    setup_tool.unsetLastVersionForProfile("imio.helpers:install-base")
