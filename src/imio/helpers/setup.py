# -*- coding: utf-8 -*-

from plone import api
from plone.dexterity.fti import DexterityFTI
from Products.GenericSetup.utils import importObjects

import logging


logger = logging.getLogger('imio.helpers.setup')


def load_workflow_from_package(wkf_name, profile_id):
    """Loads a workflow from his xml definition.
    :param wkf_name: workflow id
    :param profile_id: package profile id
    :return: status as boolean
    """
    wkf_tool = api.portal.get_tool('portal_workflow')
    wkf_obj = wkf_tool.get(wkf_name)
    if wkf_obj is None:
        logger.error("Cannot find '{}' workflow name in portal".format(wkf_name))
        return False
    ps_tool = api.portal.get_tool('portal_setup')
    try:
        context = ps_tool._getImportContext(profile_id, True)
    except KeyError:
        logger.error("Cannot find '{}' profile id".format(profile_id))
        return False
    # ps_tool.applyContext(context)  # necessary ?
    importObjects(wkf_obj, 'workflows/', context)
    if wkf_obj._p_changed is False:
        logger.error("Could not update '{}' using profile '{}'".format(wkf_name, profile_id))
        return False
    return True


def load_type_from_package(type_name, profile_id, purge_actions=False):
    """Loads a portal_type from his xml definition.
    :param type_name: portal_type id
    :param profile_id: package profile id
    :return: status as boolean
    """
    types_tool = api.portal.get_tool('portal_types')
    portal_type = types_tool.get(type_name)
    if portal_type is None:
        logger.error("Cannot find '{}' portal_type name in portal".format(type_name))
        return False
    ps_tool = api.portal.get_tool('portal_setup')
    try:
        context = ps_tool._getImportContext(profile_id, True)
    except KeyError:
        logger.error("Cannot find '{}' profile id".format(profile_id))
        return False

    # special case for DX FTI, _should_purge is set to False or it fails when purging
    if isinstance(portal_type, DexterityFTI):
        context._should_purge = False

    if purge_actions:
        # remove actions so it is reloaded in correct order
        portal_type._actions = ()

    # ps_tool.applyContext(context)  # necessary ?
    importObjects(portal_type, 'types/', context)
    if portal_type._p_changed is False:
        logger.error("Could not update '{}' using profile '{}'".format(type_name, profile_id))
        return False
    return True
