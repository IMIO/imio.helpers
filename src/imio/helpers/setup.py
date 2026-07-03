# -*- coding: utf-8 -*-

from plone import api
from plone.api.exc import InvalidParameterError
from plone.dexterity.fti import DexterityFTI
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.utils import importObjects
from zope.component import queryMultiAdapter

import logging


logger = logging.getLogger("imio.helpers.setup")


def load_type_from_package(type_name, profile_id, purge_actions=False, create=False):
    """Loads a portal_type from his xml definition.
    :param type_name: portal_type id
    :param profile_id: package profile id
    :param purge_actions: empties type actions
    :param create: create an empty Dexterity FTI when the type does not exist yet (first load)
    :return: status as boolean
    """
    types_tool = api.portal.get_tool("portal_types")
    ps_tool = api.portal.get_tool("portal_setup")
    try:
        context = ps_tool._getImportContext(profile_id, True)
    except KeyError:
        logger.error("Cannot find '{}' profile id".format(profile_id))
        return False
    if context.readDataFile("types/%s.xml" % type_name) is None:
        logger.error("No type xml definition for '{}' in profile '{}'".format(type_name, profile_id))
        return False
    portal_type = types_tool.get(type_name)
    created = False
    if portal_type is None:
        if not create:
            logger.error("Cannot find '{}' portal_type name in portal".format(type_name))
            return False

        # first load: create an empty Dexterity FTI so importObjects can fill it from the xml
        types_tool._setObject(type_name, DexterityFTI(type_name))
        portal_type = types_tool.get(type_name)
        created = True

    # special case for DX FTI, _should_purge is set to False or it fails when purging
    if isinstance(portal_type, DexterityFTI):
        context._should_purge = False

    if purge_actions:
        # remove actions so it is reloaded in correct order
        portal_type._actions = ()

    # ps_tool.applyContext(context)  # necessary ?
    importObjects(portal_type, "types/", context)
    # a freshly created fti fills sub-attributes: _p_changed on the fti itself may stay False
    if not created and portal_type._p_changed is False:
        logger.error("Could not update '{}' using profile '{}'".format(type_name, profile_id))
        return False
    return True


def load_workflow_from_package(wkf_name, profile_id, purge_workflow=True, create=False):
    """Loads a workflow from his xml definition.
    :param wkf_name: workflow id
    :param profile_id: package profile id
    :param purge_workflow: remove states and transitions before loading
    :param create: create an empty DCWorkflow when the workflow does not exist yet (first load).
                   Note: the type/workflow binding (stored in workflows.xml) still has to be set separately.
    :return: status as boolean
    """
    wkf_tool = api.portal.get_tool("portal_workflow")
    ps_tool = api.portal.get_tool("portal_setup")
    try:
        context = ps_tool._getImportContext(profile_id, True)
    except KeyError:
        logger.error("Cannot find '{}' profile id".format(profile_id))
        return False
    if context.readDataFile("workflows/%s/definition.xml" % wkf_name) is None:
        logger.error("No workflow xml definition for '{}' in profile '{}'".format(wkf_name, profile_id))
        return False
    wkf_obj = wkf_tool.get(wkf_name)
    created = False
    if wkf_obj is None:
        if not create:
            logger.error("Cannot find '{}' workflow name in portal".format(wkf_name))
            return False
        # first load: create an empty DCWorkflow so importObjects can fill it from the xml
        wkf_tool._setObject(wkf_name, DCWorkflowDefinition(wkf_name))
        wkf_obj = wkf_tool.get(wkf_name)
        purge_workflow = False  # brand new workflow, nothing to purge
        created = True
    if purge_workflow:
        wkf_obj.states.deleteStates(list(wkf_obj.states.keys()))
        wkf_obj.transitions.deleteTransitions(list(wkf_obj.transitions.keys()))
    # ps_tool.applyContext(context)  # necessary ?
    importObjects(wkf_obj, "workflows/", context)
    logger.info("'%s' workflow info imported", wkf_name)
    # a freshly created workflow fills its states/transitions sub-objects: _p_changed on the
    # workflow itself may stay False
    if not created and wkf_obj._p_changed is False:
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
    ps_tool = api.portal.get_tool("portal_setup")
    try:
        context = ps_tool._getImportContext(profile_id, False)  # do not purge !
    except KeyError:
        logger.error("Cannot find '{}' profile id".format(profile_id))
        return False
    # ps_tool.applyContext(context)  # necessary ?
    importer = queryMultiAdapter((tool, context), IBody)
    path = tool_name.replace(" ", "_")
    __traceback_info__ = path
    if importer:
        if importer.name:
            path = importer.name
        filename = "%s%s" % (path, importer.suffix)
        body = context.readDataFile(filename)
        if body is not None:
            importer.filename = filename  # for error reporting
            importer.body = body
    if tool._p_changed is False:
        logger.error("Could not update '{}' using profile '{}'".format(tool_name, profile_id))
        return False
    return True


def remove_gs_step(step_id, registry="_import_registry"):
    """Remove a step from a generic setup registry.
    :param step_id: import step id
    :param registry: registry name (default: _import_registry)
    :return: status as boolean
    """
    ps_tool = api.portal.get_tool("portal_setup")
    if not hasattr(ps_tool, registry):
        logger.error("Cannot find '{}' registry in portal_setup".format(registry))
        return False
    registry = getattr(ps_tool, registry)
    if step_id in registry.listSteps():
        registry.unregisterStep(step_id)
        ps_tool._p_changed = True
        return True
    return False
