# -*- coding: utf-8 -*-
from plone import api
from zope.component import getMultiAdapter


class ListContainedDexterityObjectsForDisplayAdapter(object):
    """ Return the dexterity objects contained, moreover the returned
        elements are renderable for display.
        element.context is the contained object
        element.widgets are the renderable widgets of the object
    """

    def __init__(self, context):
        self.context = context

    def listContainedObjects(self, portal_types=(), widgets_to_render=(), b_start=0, b_size=30):
        """ Return a list of renderable objects.
            If p_portal_types is given, filter on portal_type in the catalog query.
            If p_widgets_to_render is given, only render given fields/widgets."""
        res = []
        params = {}
        params['path'] = {'query': '/'.join(self.context.getPhysicalPath()),
                          'depth': 1}
        params['sort_on'] = 'getObjPositionInParent'
        # make sure we only list dexterity objects
        params['object_provides'] = 'plone.dexterity.interfaces.IDexterityContent'

        if portal_types:
            params['portal_type'] = portal_types
        request = self.context.REQUEST
        i = 0
        catalog = api.portal.get_tool('portal_catalog')
        for brain in catalog(**params):
            # manage the batch to avoid rendering elements that are not shown
            # manage elements before currently shown ones...
            # and manage elements after currently shown ones
            if b_start and i < b_start or \
               i > (b_start + b_size):
                i = i + 1
                res.append(None)
                continue

            obj = brain.getObject()
            renderedAction = getMultiAdapter((obj, request), name='view')
            renderedAction.updateFieldsFromSchemata()
            for field in renderedAction.fields:
                if widgets_to_render and field not in widgets_to_render:
                    renderedAction.fields = renderedAction.fields.omit(field)
            renderedAction.updateWidgets()
            res.append(renderedAction)
            i = i + 1
        return res
