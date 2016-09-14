# -*- coding: utf-8 -*-

import os

from plone import api
from plone.app.textfield.value import RichTextValue
from plone.namedfile.file import NamedBlobImage

from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone.utils import safe_unicode

import logging
logger = logging.getLogger('imo.helpers.content')


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


def add_image(obj, filepath='', img_obj=None):
    """
        Add a lead image or an image on object
    """
    if filepath:
        filename = os.path.basename(filepath)
        namedblobimage = NamedBlobImage(data=open(filepath, 'r').read(), filename=safe_unicode(filename))
    elif img_obj:
        namedblobimage = img_obj.image
    setattr(obj, 'image', namedblobimage)

# Define a global variable to can be used in create function, following globl param
cids_g = {}


def create(conf, cids={}, globl=False):
    """
        Create objects following configuration.
        :param conf: list of dict. A dict is an object to create
            Example (* = is mandatory)
            [
                {
                'cid': 1,  # configuration id
            *   'cont': cid or 'path',  # container: can be cid or previous created object or relative path
            *   'type': portal type,  # portal_type
                'id': 'toto',  # if not set in dic, id will be generated from title
            *   'title': 'Toto',
                'trans': ['transition1', 'transition2']  # if set, we will try to apply the different transitions
                'attrs': {}  # dictionnary of other attributes
                'functions': [add_image]  # list of functions that will be called with obj as first parameter
                'extra': {'add_image': {}}}  # extra kwargs passed to each function
                }
            ]
        :param cids: dict containing as key a 'cid' and as value 'an object'
        :param globl: indicate if cid => object relations will be globally used for this call
    """
    cids_l = {}
    if globl:
        cids_l = cids_g
    cids_l.update(cids)

    portal = api.portal.getSite()
    ppath = '/'.join(portal.getPhysicalPath())

    for i, dic in enumerate(conf):
        container = dic['cont']
        if isinstance(container, int):
            parent = cids_l.get(container, None)
        elif isinstance(container, str):
            container = container.strip('/ ')
            if container:
                parent = get_object(path='%s/%s' % (ppath, container))
            else:
                parent = portal
        if not parent:
            logger.error("Dict nb %d: cannot find container %s (cid=%d)" % (i, container, dic['cid']))
            continue
        obj = get_object(parent='/'.join(parent.getPhysicalPath()), type=dic['type'], title=dic.get('title', ''),
                         id=dic.get('id', ''))
        if not obj:
            obj = api.content.create(container=parent, type=dic['type'], title=safe_unicode(dic['title']),
                                     id=dic.get('id', None), safe_id=bool(dic.get('id', '')),
                                     **dic.get('attrs', {}))
        if 'cid' in dic:
            cids_l[dic['cid']] = obj
        transitions(obj, dic['trans'])
        for fct in dic.get('functions', []):
            params = dic.get('extra', {}).get(fct.__name__, {})
            fct(obj, **params)
    return cids_l


def richtextval(text):
    """
        Return a RichTextValue to be stored in IRichText field
    """
    return RichTextValue(raw=safe_unicode(text), mimeType='text/html', outputMimeType='text/html', encoding='utf-8')
