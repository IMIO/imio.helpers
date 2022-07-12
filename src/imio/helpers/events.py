# -*- coding: utf-8 -*-

from imio.helpers.cache import invalidate_cachekey_volatile_for


def onPrincipalCreated(event):
    """Invalidate the cachekey that manages users/groups associations."""
    invalidate_cachekey_volatile_for('_users_groups_value', get_again=True)


def onPrincipalDeleted(event):
    """Invalidate the cachekey that manages users/groups associations."""
    invalidate_cachekey_volatile_for('_users_groups_value', get_again=True)


def onPrincipalModified(event):
    """Invalidate the cachekey that manages users/groups associations."""
    invalidate_cachekey_volatile_for('_users_groups_value', get_again=True)


def onPrincipalAddedToGroup(event):
    """Invalidate the cachekey that manages users/groups associations."""
    invalidate_cachekey_volatile_for('_users_groups_value', get_again=True)


def onPrincipalRemovedFromGroup(event):
    """Invalidate the cachekey that manages users/groups associations."""
    invalidate_cachekey_volatile_for('_users_groups_value', get_again=True)


def onGroupCreated(event):
    """Invalidate the cachekey that manages users/groups associations."""
    invalidate_cachekey_volatile_for('_users_groups_value', get_again=True)


def onGroupDeleted(event):
    """Invalidate the cachekey that manages users/groups associations."""
    invalidate_cachekey_volatile_for('_users_groups_value', get_again=True)
