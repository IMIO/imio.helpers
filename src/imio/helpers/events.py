# -*- coding: utf-8 -*-

from imio.helpers.cache import invalidate_cachekey_volatile_for


def onPrincipalAddedToGroup(event):
    """Invalidate the cachekey that manages users/groups associations."""
    invalidate_cachekey_volatile_for(
        'Products.PloneMeeting.ToolPloneMeeting._users_groups_value', get_again=True)


def onPrincipalRemovedFromGroup(event):
    """Invalidate the cachekey that manages users/groups associations."""
    invalidate_cachekey_volatile_for(
        'Products.PloneMeeting.ToolPloneMeeting._users_groups_value', get_again=True)
