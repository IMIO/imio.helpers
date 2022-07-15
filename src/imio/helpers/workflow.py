# -*- coding: utf-8 -*-

from plone import api
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone.utils import safe_unicode
from zope.i18n import translate

import logging


logger = logging.getLogger('imio.helpers.wokflow')


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
