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


def get_leading_transitions(wf, state_id, not_starting_with=None):
    """Returns transitions leading to a WF state.

    :param wf: wf object
    :param state_id: leading state id
    :param not_starting_with: transition id starting string
    :return: a list of WFtransitions
    """
    res = []
    for tr in wf.transitions.values():
        if tr.new_state_id == state_id and \
           (not_starting_with is None or not tr.id.startswith(not_starting_with)):
            res.append(tr)
    return res


def remove_state_transitions(wf_name, state_id, remv_trs=[]):
    """Removes transitions defined on a state and possible duplicates

    :param wf_name: workflow string name
    :param state_id: state id
    :param remv_trs: list of transitions to remove
    :return: True if removed
    """
    wf_tool = api.portal.get_tool('portal_workflow')
    # if wf_name not in wf_tool:  # prefer an exception...
    wf = wf_tool[wf_name]
    if state_id not in wf.states:
        return False
    state = wf.states[state_id]
    orig_len = len(state.transitions)
    trs = []
    # keep right transitions and remove duplicates
    [trs.append(tr) for tr in list(state.transitions) if tr not in remv_trs and tr not in trs]
    if len(trs) != orig_len:
        state.transitions = tuple(trs)
        return True
    return False


def update_role_mappings_for(obj, wf=None):
    """Update role mappings regarding WF definition.
       If updated, the security indexes are reindexed.

    :param wf: the obj workflow
    :param obj: object to update role mappings for
    """
    if not wf:
        wf_tool = api.portal.get_tool('portal_workflow')
        wf = wf_tool.getWorkflowsFor(obj)[0]
    updated = wf.updateRoleMappingsFor(obj)
    if updated:
        obj.reindexObjectSecurity()
    return updated


def get_final_states(wf, ignored_transition_prefix='back', ignored_transition_ids=[]):
    """Return the final states of a workflow.
       Final states are states with only "back" transitions.
    :param wf: the obj workflow
    :param ignored_transition_prefix: the prefix of transitions to ignore,
    considered as "back" transitions
    :param ignored_transition_ids: some specific transition ids to ignore
    :return: True if removed
    """
    res = []
    for state in wf.states.values():
        not_final_transitions = [
            tr for tr in state.transitions
            if not tr.startswith(ignored_transition_prefix) and
            tr not in ignored_transition_ids]
        # no other transitions left, then it is a final state
        if not not_final_transitions:
            res.append(state.id)
    return res
