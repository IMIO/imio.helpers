# -*- coding: utf-8 -*-

from persistent.list import PersistentList
from plone import api
from plone.api.validation import mutually_exclusive_parameters
from plone.app.textfield.value import RichTextValue
from plone.behavior.interfaces import IBehavior
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from plone.registry.interfaces import IRegistry
from Products.CMFCore.interfaces import IPropertiesTool
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone.utils import getFSVersionTuple
from Products.CMFPlone.utils import safe_unicode
from zope.annotation import IAnnotations
from zope.component import getUtility
from zope.component import queryUtility
from zope.interface.interfaces import IMethod
from zope.schema._field import Bool

import logging
import os


HAS_PLONE5 = bool(getFSVersionTuple()[0] >= 5)
if HAS_PLONE5:
    from Products.CMFPlone.interfaces import IEditingSchema

logger = logging.getLogger('imio.helpers.content')
ADDED_TYPE_ERROR = 'A validation error occurred while instantiating "{0}" with id "{1}". {2}'


def get_object(parent='', id='', title='', type='', obj_path=''):
    """
    Find an object following parameters
    :param id: searched id.
    :type id: string

    :param type: searched portal type.
    :type type: string

    :param title: searched title.
    :type title: string

    :param obj_path: searched relative path.
    :type obj_path: string

    :param parent: object parent (can be the object or the relative path).
    :type type: object or string

    :returns: Content object
    """
    portal = api.portal.getSite()
    ppath = '/'.join(portal.getPhysicalPath())
    pc = portal.portal_catalog
    params = {}
    if obj_path == '/':
        return portal
    elif obj_path:
        params['path'] = {'query': '%s/%s' % (ppath, obj_path.strip('/')), 'depth': 0}
    elif parent:
        if isinstance(parent, str):
            params['path'] = {'query': '%s/%s' % (ppath, parent.strip('/')), 'depth': 1}
        else:
            params['path'] = {'query': '/'.join(parent.getPhysicalPath()), 'depth': 1}
    if id:
        params['id'] = id
    if title:
        params['Title'] = title
    if type:
        params['portal_type'] = type
    brains = pc.unrestrictedSearchResults(**params)
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


def create_NamedBlob(filepath, typ='file'):
    """
        Return a NamedBlobFile or NamedBlobImage
        typ = 'file' or 'img'
    """
    if typ == 'file':
        klass = NamedBlobFile
    elif typ == 'img':
        klass = NamedBlobImage
    filename = os.path.basename(filepath)
    fh = open(filepath, 'r')
    namedblob = klass(data=fh.read(), filename=safe_unicode(filename))
    fh.close()
    return namedblob


def add_image(obj, attr='image', filepath='', img_obj=None, obj_attr=None, contentType=''):
    """
        Add a lead image or an image on dexterity object
    """
    if filepath:
        namedblobimage = create_NamedBlob(filepath, typ='img')
    elif img_obj:
        if not obj_attr:
            obj_attr = attr
        namedblobimage = getattr(img_obj, obj_attr)
    setattr(obj, attr, namedblobimage)


def add_file(obj, attr='file', filepath='', file_obj=None, obj_attr=None, contentType=''):
    """
        Add a blob file on dexterity object
    """
    if filepath:
        namedblobfile = create_NamedBlob(filepath)
    elif file_obj:
        if not obj_attr:
            obj_attr = attr
        namedblobfile = getattr(file_obj, obj_attr)
    setattr(obj, attr, namedblobfile)


# Define a global variable to can be used in create function, following globl param
cids_g = {}


def create(conf, cids={}, globl=False, pos=False, clean_globl=False):
    """
    Create objects following configuration.
        :param conf: list of dict. A dict is an object to create
            Description (* = is mandatory)
            [
                {
                'cid': 1,  # configuration id, integer > 0 !
            *   'cont': cid or 'path',  # container: can be cid of previous created object or relative path
            *   'type': portal type,  # portal_type
                'id': 'toto',  # if not set in dic, id will be generated from title
            *   'title': 'Toto',
                'trans': ['transition1', 'transition2']  # if set, we will try to apply the different transitions
                'attrs': {}  # dictionnary of other attributes
                'functions': [(add_image, args, kwargs)]  # list of functions/methods called on created obj.
                                                          # args is a list of positional params.
                                                          # kwargs is a dict of named params.
                }
            ]
        :param cids: dict containing as key a 'cid' and as value 'an object'
        :param globl: indicate if cid - object relations will be globally used for this call (default: False)
        :param pos: set created objects at list position. (default: True)
        :param clean_globl: clean global dic

        :return cids dict

    Example:
        create([{'cid': 1, 'cont': 0, 'title': 'Welcome', 'type': 'mytype',
                 'attrs': {'text': richtextval('<h1>Welcome</h1>')},
                 'functions': [(add_file, [], {'filepath': 'xxx'})]}],
                 cids={0: portal})
    """
    cids_l = {}
    if clean_globl:
        global cids_g
        cids_g = {}
    if globl:
        cids_l = cids_g
    cids_l.update(cids)

    for i, dic in enumerate(conf):
        container = dic['cont']
        if 'cid' in dic:
            cid = dic['cid']
            if not isinstance(cid, int) or not cid > 0:
                raise ValueError("Dict nb %s: cid '%s' must be an integer > 0" % (i, cid))
        else:
            cid = 0
        if isinstance(container, int):
            parent = cids_l.get(container, None)
        elif isinstance(container, str):
            parent = get_object(obj_path=container)
        if not parent:
            raise ValueError("Dict nb %s: cannot find container '%s')" % ((cid and '%s (cid=%s)' % (i, cid) or i),
                             container))
        if dic.get('id', ''):
            obj = get_object(parent=parent, id=dic.get('id'))
        else:
            obj = get_object(parent=parent, type=dic['type'], title=dic.get('title'))
        if not obj:
            obj = api.content.create(container=parent, type=dic['type'], title=safe_unicode(dic['title']),
                                     id=dic.get('id', None), safe_id=not bool(dic.get('id', '')),
                                     **dic.get('attrs', {}))
            for fct, args, kwargs in dic.get('functions', []):
                fct(obj, *args, **kwargs)
        if cid:
            cids_l[cid] = obj
        transitions(obj, dic.get('trans', []))
        # set at right position
        if pos and parent.getObjectPosition(obj.getId()) != i:
            parent.moveObjectToPosition(obj.getId(), i)
    return cids_l


def richtextval(text):
    """
        Return a RichTextValue to be stored in IRichText field
    """
    return RichTextValue(raw=safe_unicode(text), mimeType='text/html', outputMimeType='text/html', encoding='utf-8')


@api.validation.at_least_one_of('obj', 'type_name')
def get_schema_fields(obj=None, type_name=None, behaviors=True):
    """
        Get all fields on content or type from its schema and its behaviors.
        Return a list of field name and field object.
    """
    portal_types = api.portal.get_tool('portal_types')
    if obj:
        type_name = obj.portal_type
    try:
        fti = portal_types[type_name]
    except:
        return []
    fti_schema = fti.lookupSchema()
    fields = [field for field in fti_schema.namesAndDescriptions(all=True)
              if not IMethod.providedBy(field)]

    if not behaviors:
        return fields

    # also lookup behaviors
    for behavior_id in fti.behaviors:
        behavior = getUtility(IBehavior, behavior_id).interface
        fields.extend(behavior.namesAndDescriptions(all=True))
    # keep only fields as interface methods are also returned by namesAndDescriptions
    fields = [(field_name, field) for (field_name, field) in fields
              if not IMethod.providedBy(field)]
    return fields


def validate_fields(obj, behaviors=True, raise_on_errors=False):
    """
       Validates every fields of given p_obj.
    """
    fields = get_schema_fields(obj=obj, behaviors=True)
    errors = []
    for (field_name, field) in fields:
        field = field.bind(obj)
        value = getattr(obj, field_name)
        # accept None for most of fields if required=False
        if value is None and not field.required and not (isinstance(field, (Bool, ))):
            continue
        # we sadly have to bypass validation for field having a source as it fails
        # because in plone.formwidget.contenttree source.py
        # self._getBrainByToken('/'.join(value.getPhysicalPath()))
        # raises 'RelationValue' object has no attribute 'getPhysicalPath'
        if hasattr(field, 'source') and field.source is not None:
            logger.warn("Bypassing validation of field {0} of {1}".format(
                field_name, '/'.join(obj.getPhysicalPath())))
            continue
        try:
            field._validate(value)
        except Exception, exc:
            errors.append(exc)
    if raise_on_errors and errors:
        error_msg = ADDED_TYPE_ERROR.format(
            obj.portal_type, obj.id, '\n'.join([repr(error) for error in errors]))
        raise ValueError(error_msg)
    return errors


def safe_encode(value, encoding='utf-8'):
    """
        Converts a value to encoding, only when it is not already encoded.
    """
    if isinstance(value, unicode):
        return value.encode(encoding)
    return value


@mutually_exclusive_parameters('obj', 'uid')
def add_to_annotation(annotation_key, value, obj=None, uid=None):
    """ Add annotation related to obj or uid """
    if not obj:
        obj = api.content.get(UID=uid)
        # api.content.get may return None
        if not obj:
            return

    annot = IAnnotations(obj)
    if annotation_key not in annot:
        annot[annotation_key] = PersistentList()
    if value not in annot[annotation_key]:
        annot[annotation_key].append(value)


@mutually_exclusive_parameters('obj', 'uid')
def del_from_annotation(annotation_key, value, obj=None, uid=None):
    """ Delete annotation related to obj or uid """
    if not obj:
        obj = api.content.get(UID=uid)
        # api.content.get may return None
        if not obj:
            return

    annot = IAnnotations(obj)
    if annotation_key not in annot:
        return
    if value in annot[annotation_key]:
        annot[annotation_key].remove(value)


@mutually_exclusive_parameters('obj', 'uid')
def get_from_annotation(annotation_key, obj=None, uid=None, default=None):
    """ Get annotation related to obj or uid """
    if not obj:
        obj = api.content.get(UID=uid)
        if not obj:
            return default

    annot = IAnnotations(obj)
    if annotation_key not in annot:
        return default
    return annot[annotation_key]


def uuidsToCatalogBrains(uuids=[], ordered=False):
    """ Given a list of UUIDs, attempt to return catalog brains,
        keeping original uuids list order if ordered=True. """

    catalog = api.portal.get_tool('portal_catalog')

    brains = catalog(UID=uuids)

    if ordered:
        # we need to sort found brains according to uuids
        def getKey(item):
            return uuids.index(item.UID)
        brains = sorted(brains, key=getKey)

    return brains


def uuidsToObjects(uuids=[], ordered=False):
    """ Given a list of UUIDs, attempt to return content objects,
        keeping original uuids list order if ordered=True. """

    brains = uuidsToCatalogBrains(uuids, ordered=ordered)
    return [brain.getObject() for brain in brains]


def disable_link_integrity_checks():
    """ """
    ptool = queryUtility(IPropertiesTool)
    site_props = getattr(ptool, 'site_properties', None)
    original_link_integrity = False
    if site_props and site_props.hasProperty(
            'enable_link_integrity_checks'):
        original_link_integrity = site_props.getProperty(
            'enable_link_integrity_checks', False)
        site_props.manage_changeProperties(
            enable_link_integrity_checks=False)
    else:
        # Plone 5
        registry = getUtility(IRegistry)
        editing_settings = registry.forInterface(IEditingSchema, prefix='plone')
        original_link_integrity = editing_settings.enable_link_integrity_checks
        editing_settings.enable_link_integrity_checks = False
    return original_link_integrity


def restore_link_integrity_checks(original_link_integrity):
    """ """
    ptool = queryUtility(IPropertiesTool)
    site_props = getattr(ptool, 'site_properties', None)
    if site_props and site_props.hasProperty(
            'enable_link_integrity_checks'):
        ptool = queryUtility(IPropertiesTool)
        site_props = getattr(ptool, 'site_properties', None)
        site_props.manage_changeProperties(
            enable_link_integrity_checks=original_link_integrity
        )
    else:
        registry = getUtility(IRegistry)
        editing_settings = registry.forInterface(IEditingSchema, prefix='plone')
        editing_settings.enable_link_integrity_checks = original_link_integrity
