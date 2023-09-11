# -*- coding: utf-8 -*-

from imio.helpers.cache import _generate_modified_portal_type_volatile_name
from imio.helpers.cache import invalidate_cachekey_volatile_for
from zope.container.contained import ContainerModifiedEvent


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


def onObjAdded(obj, event):
    """Invalidate "modified" cachekey when a transition occured."""
    invalidate_cachekey_volatile_for(
        _generate_modified_portal_type_volatile_name(obj.portal_type),
        get_again=True)


def onObjInitialized(obj, event):
    """Invalidate "modified" cachekey when a transition occured.
       For AT, plone.restapi calls it but not the "ObjectAdded" event."""
    invalidate_cachekey_volatile_for(
        _generate_modified_portal_type_volatile_name(obj.portal_type),
        get_again=True)


def onObjModified(obj, event):
    """Invalidate "modified" cachekey when a transition occured."""
    # we bypass if called because content was changed,
    # like contained object added/removed
    if not isinstance(event, ContainerModifiedEvent):
        invalidate_cachekey_volatile_for(
            _generate_modified_portal_type_volatile_name(obj.portal_type),
            get_again=True)


def onObjRemoved(obj, event):
    """Invalidate "modified" cachekey when a transition occured."""
    invalidate_cachekey_volatile_for(
        _generate_modified_portal_type_volatile_name(obj.portal_type),
        get_again=True)


def onObjTransition(obj, event):
    """Invalidate "modified" cachekey when a transition occured."""
    if not event.transition or (obj != event.object):
        return
    invalidate_cachekey_volatile_for(
        _generate_modified_portal_type_volatile_name(obj.portal_type),
        get_again=True)
