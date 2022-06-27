# -*- coding: utf-8 -*-
from plone import api
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone.utils import safe_unicode
from Products.GenericSetup.utils import importObjects
from zope.i18n import translate

import logging


logger = logging.getLogger('imio.helpers.content')


def do_transitions(obj, transitions, warn=False):
    """
        Apply multiple transitions on obj
    """
    wkf_tool = api.portal.get_tool("portal_workflow")
    if not isinstance(transitions, (list, tuple)):
        transitions = [transitions]
    for tr in transitions:
        try:
            wkf_tool.doActionFor(obj, tr)
        except WorkflowException as exc:
            if warn:
                logger.warn("Cannot apply transition '%s' on obj '%s': '%s'" % (tr, obj, exc))


def get_state_infos(obj):
    """ """
    wkf_tool = api.portal.get_tool('portal_workflow')
    review_state = wkf_tool.getInfoFor(obj, 'review_state')
    wf = wkf_tool.getWorkflowsFor(obj)[0]
    state = wf.states.get(review_state)
    state_title = state and state.title or review_state
    return {'state_name': review_state,
            'state_title': translate(safe_unicode(state_title),
                                     domain="plone",
                                     context=obj.REQUEST)}


def get_transitions(obj):
    """Return the ids of the available transitions as portal_workflow.getTransitionsFor
       will actually return a list of dict with various infos (id, title, name, ...) of
       the available transitions."""
    wf_tool = api.portal.get_tool('portal_workflow')
    return [tr["id"] for tr in wf_tool.getTransitionsFor(obj)]


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
    try:
        importObjects(wkf_obj, 'workflows/', context)
    except Exception as err:
        logger.error("Cannot import xml: '{}'".format(err))
        return False
    return True
