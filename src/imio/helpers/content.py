# -*- coding: utf-8 -*-

from plone import api
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone.utils import safe_unicode

import logging
logger = logging.getLogger('imo.helpers.content')

"""
Exemple config object
[
    {
    'cid': 1,  # configuration id
    'cont': cid or 'path',  # container: can be cid or previous created object or relative path
    'typ': portal type,  # portal_type
    'id': 'toto',  # if not set in dic, id will be generated from title
    'title': 'Toto',
    'trans': ['transition1', 'transition2']  # if set, we will try to apply the different transitions
    'attrs': {}  # dictionnary of other attributes
    'functions': []  # list of functions that will be called with obj as first parameter
    'extra': {}  # extra kwargs passed to each function
    }
]
"""


def get_object(parent='', id='', title='', type='', path=''):
    pc = api.portal.get_tool('portal_catalog')
    params = {}
    if path:
        params['path'] = {'query': path, 'depth': 0}
    elif parent:
        params['path'] = {'query': parent, 'depth': 1}
    if id:
        params['id'] = id
    if title:
        params['Title'] = title
    if type:
        params['portal_type'] = type
    brains = pc(**params)
    if brains:
        return brains[0].getObject()
    return None


def transitions(obj, transitions):
    """
        Apply multiple transitions on obj
    """
    workflowTool = api.portal.get_tool("portal_workflow")
    if not isinstance(transitions, (list, tuple)):
        transitions = [transitions]
    for tr in transitions:
        try:
            workflowTool.doActionFor(obj, tr)
        except WorkflowException:
            logger.warn("Cannot apply transition '%s' on obj '%s'" % (tr, obj))


def create(conf, cids={}):
    """
        Create objects following configuration
    """
    portal = api.portal.getSite()
    ppath = '/'.join(portal.getPhysicalPath())

    for i, dic in enumerate(conf):
        container = dic['cont']
        if isinstance(container, int):
            parent = cids.get(container, None)
        elif isinstance(container, str):
            parent = get_object(path='%s/%s' % (ppath, (container.startswith('/') and container[1:] or container)))
        if not parent:
            logger.error("Dict nb %d: cannot find container %s (cid=%d)" % (i, container, dic['cid']))
            continue
        obj = get_object(parent='/'.join(parent.getPhysicalPath()), type=dic['typ'], title=dic.get('title', ''),
                         id=dic.get('id', ''))
        if not obj:
            obj = api.content.create(container=parent, type=dic['typ'], title=safe_unicode(dic['title']),
                                     id=dic.get('id', None), safe_id=bool(dic.get('id', '')),
                                     **dic.get('attrs', {}))
        cids[dic['cid']] = obj
        transitions(obj, dic['trans'])
    return cids
