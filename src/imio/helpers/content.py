# -*- coding: utf-8 -*-

from imio.helpers.interfaces import IContainerOfUnindexedElementsMarker
from persistent.list import PersistentList
from plone import api
from plone.api.content import _parse_object_provides_query
from plone.api.validation import mutually_exclusive_parameters
from plone.app.textfield.value import RichTextValue
from plone.behavior.interfaces import IBehavior
from plone.i18n.normalizer.interfaces import IUserPreferredURLNormalizer
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from plone.registry.interfaces import IRegistry
from Products.CMFCore.interfaces import IPropertiesTool
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import getFSVersionTuple
from Products.CMFPlone.utils import safe_unicode
from zc.relation.interfaces import ICatalog
from zope.annotation import IAnnotations
from zope.component import getUtility
from zope.component import queryUtility
from zope.i18n import translate
from zope.interface.interfaces import IMethod
from zope.intid.interfaces import IIntIds
from zope.schema._field import Bool
from zope.schema.interfaces import IVocabularyFactory

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


def transitions(obj, transitions, warn=False):
    """
        Apply multiple transitions on obj
    """
    workflowTool = api.portal.get_tool("portal_workflow")
    if not isinstance(transitions, (list, tuple)):
        transitions = [transitions]
    for tr in transitions:
        try:
            workflowTool.doActionFor(obj, tr)
        except WorkflowException as exc:
            if warn:
                logger.warn("Cannot apply transition '%s' on obj '%s': '%s'" % (tr, obj, exc))


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
        :param pos: set created objects at list position. (default: False)
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


def richtextval(text, mimeType=u"text/html", outputMimeType=u"text/x-html-safe"):
    """
        Return a RichTextValue to be stored in IRichText field
    """
    return RichTextValue(raw=safe_unicode(text),
                         mimeType=mimeType,
                         outputMimeType=outputMimeType,
                         encoding='utf-8')


@api.validation.at_least_one_of('obj', 'type_name')
def get_schema_fields(obj=None, type_name=None, behaviors=True, prefix=False):
    """
        Get all fields on dexterity content or type from its schema and its behaviors.
        Return a list of field name and field object.
    """
    portal_types = api.portal.get_tool('portal_types')
    if obj:
        type_name = obj.portal_type
    try:
        fti = portal_types[type_name]
    except KeyError:
        return []
    fti_schema = fti.lookupSchema()
    fields = [(field_name, field) for (field_name, field) in fti_schema.namesAndDescriptions(all=True)
              if not IMethod.providedBy(field)]

    if not behaviors:
        return fields

    # also lookup behaviors
    for behavior_id in fti.behaviors:
        behavior = getUtility(IBehavior, behavior_id).interface
        for (field_name, field) in behavior.namesAndDescriptions(all=True):
            # keep only fields as interface methods are also returned by namesAndDescriptions
            if IMethod.providedBy(field):
                continue
            if prefix:
                field_name = '{}.{}'.format(behavior.__name__, field_name)
            fields.append((field_name, field))
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
        except Exception as exc:
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
    return value


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
    return value


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


@mutually_exclusive_parameters('obj', 'uid')
def set_to_annotation(annotation_key, value, obj=None, uid=None):
    """ Set annotation related to obj or uid """
    if not obj:
        obj = api.content.get(UID=uid)
        if not obj:
            return

    annot = IAnnotations(obj)
    annot[annotation_key] = value
    return value


def uuidsToCatalogBrains(uuids=[],
                         ordered=False,
                         query={},
                         check_contained_uids=False,
                         unrestricted=False):
    """ Given a list of UUIDs, attempt to return catalog brains,
        keeping original uuids list order if p_ordered=True.
        If p_check_contained_uids=True, if we do not find brains using the UID
        index, we will try to get it using the contained_uids index, used when
        subelements are not indexed."""

    catalog = api.portal.get_tool('portal_catalog')
    searcher = catalog.searchResults
    if unrestricted:
        searcher = catalog.unrestrictedSearchResults

    brains = searcher(UID=uuids, **query)

    if not brains and check_contained_uids and 'contained_uids' in catalog.Indexes:
        brains = searcher(contained_uids=uuids, **query)

    if ordered:
        # we need to sort found brains according to uuids
        def getKey(item):
            return uuids.index(item.UID)
        brains = sorted(brains, key=getKey)

    return brains


def uuidToCatalogBrain(uuid,
                       ordered=False,
                       query={},
                       check_contained_uids=False,
                       unrestricted=False):
    """Shortcut to call uuidsToCatalogBrains to get one single element."""
    res = uuidsToCatalogBrains(
        uuids=[uuid],
        ordered=ordered,
        query=query,
        check_contained_uids=check_contained_uids,
        unrestricted=unrestricted)
    if res:
        res = res[0]
    return res


def _contained_objects(obj, only_unindexed=False):
    """Return every elements contained in p_obj, incuding sub_elements.
       If p_only_unindexed=True, then we only return elements that are not indexed"""
    if only_unindexed and not IContainerOfUnindexedElementsMarker.providedBy(obj):
        return []

    def get_objs(container, objs=[]):
        for subcontainer in container.objectValues():
            if not only_unindexed or \
               (only_unindexed and subcontainer._getCatalogTool() is None):
                objs.append(subcontainer)
            get_objs(subcontainer, objs)
        return objs
    return get_objs(obj)


def uuidsToObjects(uuids=[], ordered=False, query={}, check_contained_uids=False, unrestricted=False):
    """ Given a list of UUIDs, attempt to return content objects,
        keeping original uuids list order if p_ordered=True.
        If p_check_contained_uids=True, if we do not find brains using the UID
        index, we will try to get it using the contained_uids index, used when
        subelements are not indexed. """

    brains = uuidsToCatalogBrains(uuids,
                                  ordered=not check_contained_uids and ordered or False,
                                  query=query,
                                  check_contained_uids=check_contained_uids,
                                  unrestricted=unrestricted)
    res = []
    if check_contained_uids:
        need_reorder = False
        for brain in brains:
            obj = brain._unrestrictedGetObject()
            if obj.UID() not in uuids:
                # it means we have a brain using a contained_uids
                for contained in _contained_objects(obj):
                    if contained.UID() in uuids:
                        need_reorder = True
                        res.append(contained)
            else:
                res.append(obj)
        if ordered and need_reorder:
            # need to sort here as disabled when calling uuidsToCatalogBrains
            def getKey(item):
                return uuids.index(item.UID())
            res = sorted(res, key=getKey)
    else:
        res = [brain._unrestrictedGetObject() for brain in brains]
    return res


def uuidToObject(uuid,
                 ordered=False,
                 query={},
                 check_contained_uids=False,
                 unrestricted=False):
    """Shortcut to call uuidsToObjects to get one single element."""
    res = uuidsToObjects(
        uuids=[uuid],
        ordered=ordered,
        query=query,
        check_contained_uids=check_contained_uids,
        unrestricted=unrestricted)
    if res:
        res = res[0]
    return res


def find(context=None, depth=None, unrestricted=False, **kwargs):
    """Same as api.content.find... but possibly unrestrictedly

    :param context: Context for the search
    :type obj: Content object
    :param depth: How far in the content tree we want to search from context
    :type obj: Content object
    :param unrestricted: unrestricted flag (default=False)
    :type bool:
    :returns: Catalog brains
    :rtype: List
    """
    query = {}
    query.update(**kwargs)

    # Save the original path to maybe restore it later.
    orig_path = query.get('path')
    if isinstance(orig_path, dict):
        orig_path = orig_path.get('query')

    # Passing a context or depth overrides the existing path query,
    # for now.
    if context or depth is not None:
        # Make the path a dictionary, unless it already is.
        if not isinstance(orig_path, dict):
            query['path'] = {}

    # Limit search depth
    if depth is not None:
        # If we don't have a context, we'll assume the portal root.
        if context is None and not orig_path:
            context = api.portal.get()
        else:
            # Restore the original path
            query['path']['query'] = orig_path
        query['path']['depth'] = depth

    if context is not None:
        query['path']['query'] = '/'.join(context.getPhysicalPath())

    # Convert interfaces to their identifiers and also allow to query
    # multiple values using {'query:[], 'operator':'and|or'}
    obj_provides = query.get('object_provides', [])
    if obj_provides:
        query['object_provides'] = _parse_object_provides_query(obj_provides)

    # Make sure we don't dump the whole catalog.
    catalog = api.portal.get_tool('portal_catalog')
    indexes = catalog.indexes()
    valid_indexes = [index for index in query if index in indexes]
    if not valid_indexes:
        return []
    if unrestricted:
        # return a new list to avoid error if corresponding looped object is deleted
        return list(catalog.unrestrictedSearchResults(**query))
    else:
        return catalog.searchResults(**query)


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


def get_vocab(context, vocab_name, only_factory=False, **kwargs):
    """ """
    vocab_factory = getUtility(IVocabularyFactory, vocab_name)
    if only_factory:
        return vocab_factory
    vocab = vocab_factory(context, **kwargs)
    return vocab


def get_state_infos(obj):
    """ """
    wfTool = api.portal.get_tool('portal_workflow')
    review_state = wfTool.getInfoFor(obj, 'review_state')
    wf = wfTool.getWorkflowsFor(obj)[0]
    state = wf.states.get(review_state)
    state_title = state and state.title or review_state
    return {'state_name': review_state,
            'state_title': translate(safe_unicode(state_title),
                                     domain="plone",
                                     context=obj.REQUEST)}


def safe_delattr(obj, attr_name):
    """ """
    if base_hasattr(obj, attr_name):
        delattr(obj, attr_name)


def base_getattr(obj, attr_name, default=None):
    """ """
    if base_hasattr(obj, attr_name):
        return getattr(obj, attr_name, default)


def get_relations(obj, attribute=None, backrefs=False):
    """Get any kind of references and backreferences"""
    res = []
    int_id = get_intid(obj)
    if not int_id:
        return res

    relation_catalog = getUtility(ICatalog)
    if not relation_catalog:
        return res

    query = {}
    if attribute:
        # Constrain the search for certain relation-types.
        query['from_attribute'] = attribute

    if backrefs:
        query['to_id'] = int_id
    else:
        query['from_id'] = int_id

    return relation_catalog.findRelations(query)


def get_back_relations(obj, attribute=None, as_objects=True):
    back_relations = get_relations(obj, attribute=attribute, backrefs=True)
    res = [back_relation.from_object for back_relation in back_relations
           if not back_relation.isBroken()]
    return res


def get_intid(obj):
    """Return the intid of an object from the intid-catalog"""
    intids = queryUtility(IIntIds)
    if intids is None:
        return
    # check that the object has an intid, otherwise there's nothing to be done
    try:
        return intids.getId(obj)
    except KeyError:
        # The object has not been added to the ZODB yet
        return


def normalize_name(request, name):
    """Use INameFromTitle normalizer on given p_name."""
    normalizer = IUserPreferredURLNormalizer(request)
    return normalizer.normalize(name)


def get_modified_attrs(modified_event):
    """Useful in a IObjectModifiedEvent to get what fields were actually edited."""
    mod_attrs = [name for attr in modified_event.descriptions
                 for name in attr.attributes]
    return mod_attrs


def object_values(context, class_names):
    """Behaves like objectValues from Zope but as meta_type for
       DX content_type is always the same, check the contained elements class name.
       Given p_class_names may be a string or list of class names."""
    res = []
    if not hasattr(class_names, '__iter__'):
        class_names = [class_names]
    for contained in context.objectValues():
        if contained.__class__.__name__ in class_names:
            res.append(contained)
    return res


def object_ids(context, class_names):
    """Behaves like objectIds from Zope but as meta_type for
       DX content_type is always the same, check the contained element class name.
       Given p_class_names may be a string or list of class names."""
    res = []
    if not hasattr(class_names, '__iter__'):
        class_names = [class_names]
    for contained in context.objectValues():
        if contained.__class__.__name__ in class_names:
            res.append(contained.getId())
    return res


def get_user_fullname(username):
    """Get fullname without using getMemberInfo that is slow slow slow...
       We get it only from mutable_properties or authentic.
       If no fullname, return username instead nothing."""
    acl_users = api.portal.get_tool('acl_users')
    storages = [acl_users.mutable_properties._storage, ]
    # if authentic is available check it first
    if base_hasattr(acl_users, 'authentic'):
        storages.insert(0, acl_users.authentic._useridentities_by_userid)

    for storage in storages:
        data = storage.get(username, None)
        if data is not None:
            fullname = ""
            # mutable_properties
            if hasattr(data, 'get'):
                fullname = data.get('fullname')
            # authentic
            else:
                fullname = data._identities['authentic-agents'].data['fullname']
            return fullname or username
    return username


def get_transitions(obj):
    """Return the ids of the available transitions as portal_workflow.getTransitionsFor
       will actually return a list of dict with various infos (id, title, name, ...) of
       the available transitions."""
    wfTool = api.portal.get_tool('portal_workflow')
    return [tr["id"] for tr in wfTool.getTransitionsFor(obj)]
