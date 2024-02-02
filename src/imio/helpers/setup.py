# -*- coding: utf-8 -*-

from plone import api
from plone.api.exc import InvalidParameterError
from plone.dexterity.fti import DexterityFTI
from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.utils import importObjects
from zope.component import queryMultiAdapter

import logging


logger = logging.getLogger('imio.helpers.setup')


def load_type_from_package(type_name, profile_id, purge_actions=False):
    """Loads a portal_type from his xml definition.
    :param type_name: portal_type id
    :param profile_id: package profile id
    :param purge_actions: empties type actions
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


def load_xml_tool_only_from_package(tool_name, profile_id):
    """Loads a tool from his xml definition.
    :param tool_name: tool id
    :param profile_id: package profile id
    :return: status as boolean
    """
    raise NotImplementedError
    try:
        tool = api.portal.get_tool(tool_name)
    except InvalidParameterError:
        logger.error("Cannot find '{}' tool name in portal".format(tool_name))
        return False
    ps_tool = api.portal.get_tool('portal_setup')
    try:
        context = ps_tool._getImportContext(profile_id, False)  # do not purge !
    except KeyError:
        logger.error("Cannot find '{}' profile id".format(profile_id))
        return False
    # ps_tool.applyContext(context)  # necessary ?
    importer = queryMultiAdapter((tool, context), IBody)
    path = tool_name.replace(' ', '_')
    __traceback_info__ = path
    if importer:
        if importer.name:
            path = importer.name
        filename = '%s%s' % (path, importer.suffix)
        body = context.readDataFile(filename)
        if body is not None:
            importer.filename = filename  # for error reporting
            importer.body = body
    if tool._p_changed is False:
        logger.error("Could not update '{}' using profile '{}'".format(tool_name, profile_id))
        return False
    return True


def remove_gs_step(step_id, registry='_import_registry'):
    """Remove a step from a generic setup registry.
    :param step_id: import step id
    :param registry: registry name (default: _import_registry)
    :return: status as boolean
    """
    ps_tool = api.portal.get_tool('portal_setup')
    if not hasattr(ps_tool, registry):
        logger.error("Cannot find '{}' registry in portal_setup".format(registry))
        return False
    registry = getattr(ps_tool, registry)
    if step_id in registry.listSteps():
        registry.unregisterStep(step_id)
        ps_tool._p_changed = True
        return True
    return False
