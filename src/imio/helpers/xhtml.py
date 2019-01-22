# -*- coding: utf-8 -*-
from Acquisition import aq_base
from os import path
from plone import api
from plone.app.imaging.scale import ImageScale
from plone.outputfilters.browser.resolveuid import uuidToURL
from plone.outputfilters.filters.resolveuid_and_caption import ResolveUIDAndCaptionFilter
from Products.CMFPlone.utils import safe_unicode
from zope.container.interfaces import INameChooser

import cgi
import lxml.html
import os
import pkg_resources
import types
import urllib


try:
    HAS_CKEDITOR = True
    pkg_resources.get_distribution('collective.ckeditor')
except pkg_resources.DistributionNotFound:
    HAS_CKEDITOR = False


CLASS_TO_LAST_CHILDREN_NUMBER_OF_CHARS_DEFAULT = 240
# Xhtml tags that may contain content
CONTENT_TAGS = ('p', 'div', 'strong', 'span', 'strike', 'i', 'em', 'u',
                'small', 'mark', 'del', 'ins', 'sub', 'sup', 'ul', 'li')


def xhtmlContentIsEmpty(xhtmlContent, tagWithAttributeIsNotEmpty=True):
    '''This method checks if given p_xhtmlContent will produce someting on rendering.
       p_xhtmlContent can either be a string or already a lxml.html element.
       If p_tagWithAttributeIsNotEmpty is True, a tag without text but with an attribute will
       be considered not empty.'''

    # first check if xhtmlContent is not simply None or so
    isStr = isinstance(xhtmlContent, types.StringType) or isinstance(xhtmlContent, types.NoneType)
    if isStr and (not xhtmlContent or not xhtmlContent.strip()):
        return True

    if isStr:
        xhtmlContent = "<special_tag>%s</special_tag>" % xhtmlContent
        tree = lxml.html.fromstring(safe_unicode(xhtmlContent))
    else:
        tree = xhtmlContent

    def _isEmpty(child):
        # consider that child as children except for some tag type
        childAsChildren = [subchild for subchild in child.getchildren() if subchild.tag not in ('br', )]
        return not bool(child.text_content().strip()) and \
            not bool(tagWithAttributeIsNotEmpty and child.attrib) and \
            not bool(childAsChildren)

    if tree.tag == 'special_tag':
        if tree.getchildren():
            for child in tree.getchildren():
                if not _isEmpty(child):
                    return False
            return True

    # if xhtmlContent renders text or has attributes or has children, we consider it not empty
    return _isEmpty(tree)


def removeBlanks(xhtmlContent, pretty_print=False):
    '''This method will remove any blank line in p_xhtmlContent.'''
    tree = _turnToLxmlTree(xhtmlContent)
    if not isinstance(tree, lxml.html.HtmlElement):
        return xhtmlContent

    for el in tree.getchildren():
        # el can be a subtree, like <ul><li>...</li></ul> we must consider entire rendering of it
        if xhtmlContentIsEmpty(el):
            el.getparent().remove(el)
    # only return children of the <special_tag>
    return ''.join([lxml.html.tostring(x,
                                       encoding='ascii',
                                       pretty_print=pretty_print,
                                       method='html')
                    for x in tree.iterchildren()])


def _turnToLxmlTree(xhtmlContent):
    if not xhtmlContent or not xhtmlContent.strip():
        return xhtmlContent

    # surround xhtmlContent with a special tag so we are sure that tree is always
    # a list of children of this special tag
    tree = lxml.html.fromstring(safe_unicode("<special_tag>%s</special_tag>" % xhtmlContent))
    children = tree.getchildren()
    if not children:
        return xhtmlContent
    return tree


def addClassToContent(xhtmlContent, css_class, pretty_print=False):
    """Add css class attribute p_css_class to every CONTENT_TAGS of p_xhtmlContent."""
    if isinstance(xhtmlContent, lxml.html.HtmlElement):
        children = [xhtmlContent]
    else:
        tree = _turnToLxmlTree(xhtmlContent)
        if not isinstance(tree, lxml.html.HtmlElement):
            return xhtmlContent
        children = tree.getchildren()

    for child in children:
        if child.tag in CONTENT_TAGS:
            exisingCssClass = child.attrib.get('class', '')
            if exisingCssClass:
                cssClass = '{0} {1}'.format(css_class, exisingCssClass)
            else:
                cssClass = css_class
            child.attrib['class'] = cssClass

    # use encoding to 'ascii' so HTML entities are translated to something readable
    res = ''.join([lxml.html.tostring(x,
                                      encoding='ascii',
                                      pretty_print=pretty_print,
                                      method='html') for x in children])
    return res


def addClassToLastChildren(xhtmlContent,
                           classNames={'p': 'ParaKWN',
                                       'div': 'ParaKWN',
                                       'strong': '',
                                       'span': '',
                                       'strike': '',
                                       'i': '',
                                       'em': '',
                                       'u': '',
                                       'small': '',
                                       'mark': '',
                                       'del': '',
                                       'ins': '',
                                       'sub': '',
                                       'sup': '',
                                       'ol': 'podNumberItemKeepWithNext',
                                       'ul': 'podBulletItemKeepWithNext',
                                       'li': 'podItemKeepWithNext'},
                           numberOfChars=CLASS_TO_LAST_CHILDREN_NUMBER_OF_CHARS_DEFAULT,
                           pretty_print=False):
    '''This method will add a class attribute adding class correspondig to tag given in p_classNames
       to the last tags of given p_xhtmlContent.
       It only consider given p_classNames keys which are text formatting tags and will define the class
       on last tags until it contains given p_numberOfChars number of characters.
    '''
    tree = _turnToLxmlTree(xhtmlContent)
    if not isinstance(tree, lxml.html.HtmlElement):
        return xhtmlContent

    children = tree.getchildren()

    def adaptTree(children, managedNumberOfChars=0):
        """
          Recursive method that walk the children and subchildren and adapt what necessary.
        """
        # apply style on last element until we reached necessary numberOfChars or we encounter
        # a tag not in CONTENT_TAGS or we do not have a tag...
        i = 1
        stillNeedToAdaptPreviousChild = True
        numberOfChildren = len(children)
        while stillNeedToAdaptPreviousChild and i <= numberOfChildren:
            child = children[-i]
            if child.tag not in CONTENT_TAGS and not child.getchildren():
                stillNeedToAdaptPreviousChild = False
            else:
                cssClass = classNames.get(child.tag, '')
                if cssClass:
                    addClassToContent(child, cssClass)
                managedNumberOfChars += child.text_content() and len(child.text_content()) or 0
                subchildren = child.getchildren()
                if subchildren:
                    # recursion is done here
                    managedNumberOfChars = adaptTree(subchildren, managedNumberOfChars=managedNumberOfChars)

                if managedNumberOfChars >= numberOfChars:
                    stillNeedToAdaptPreviousChild = False
                i = i + 1
        return managedNumberOfChars

    # call recursive method 'adaptTree' that whill adapt children and subchildren
    adaptTree(children)

    # use encoding to 'ascii' so HTML entities are translated to something readable
    res = ''.join([lxml.html.tostring(x,
                                      encoding='ascii',
                                      pretty_print=pretty_print,
                                      method='html') for x in tree.iterchildren()])
    return res


def markEmptyTags(xhtmlContent,
                  markingClass='highlightBlankRow',
                  tagTitle='',
                  onlyAtTheEnd=False,
                  tags=('p', 'div', ),
                  pretty_print=False):
    '''This will add a CSS class p_markingClass to tags of the given p_xhtmlContent
       that are empty.  If p_onlyAtTheEnd is True, it will only mark empty rows that are
       ending the XHTML content.'''
    tree = _turnToLxmlTree(xhtmlContent)
    if not isinstance(tree, lxml.html.HtmlElement):
        return xhtmlContent

    childrenToMark = []
    # find children to mark, aka empty tags taking into account p_onlyAtTheEnd
    for child in tree.getchildren():
        if child.tag in tags and xhtmlContentIsEmpty(child, tagWithAttributeIsNotEmpty=False):
            childrenToMark.append(child)
        elif onlyAtTheEnd:
            # if tag is not managed or not empty, we reinitialize the childrenToMark
            # because we are on a tag that is not considered empty
            childrenToMark = []
    for child in childrenToMark:
        if 'class' in child.attrib:
            child.attrib['class'] = '{0} {1}'.format(markingClass, child.attrib['class'])
        else:
            child.attrib['class'] = markingClass
        # add a title to the tag if necessary
        if tagTitle:
            child.attrib['title'] = tagTitle
    return ''.join([lxml.html.tostring(x,
                                       encoding='utf-8',
                                       pretty_print=pretty_print,
                                       method='html')
                    for x in tree.iterchildren()])


def removeCssClasses(xhtmlContent,
                     css_classes=[],
                     pretty_print=False):
    ''' '''
    tree = _turnToLxmlTree(xhtmlContent)
    if not isinstance(tree, lxml.html.HtmlElement):
        return xhtmlContent

    for content_tag in CONTENT_TAGS:
        tags = tree.findall('.//{0}'.format(content_tag))
        for tag in tags:
            if 'class' in tag.attrib and tag.attrib['class'].strip() in css_classes:
                del tag.attrib['class']

    return ''.join([lxml.html.tostring(x,
                                       encoding='utf-8',
                                       pretty_print=pretty_print,
                                       method='html')
                    for x in tree.iterchildren()])


def imagesToPath(context, xhtmlContent, pretty_print=False):
    '''Turn <img> source contained in given p_xhtmlContent to a FileSystem absolute path
       to the .blob binary stored on the server.  This is usefull when generating documents
       with XHTML containing images that are private, LibreOffice is not able to access these
       images using the HTTP request.
       <img src='http://mysite/myfolder/myimage.png' /> becomes
       <img src='/absolute/path/to/blobstorage/myfile.blob'/>,
       external images are left unchanged.
       The image_scale is not kept, so :
       <img src='http://mysite/myfolder/myimage.png/image_preview' /> becomes
       <img src='/absolute/path/to/blobstorage/myfile.blob'/>.'''
    # keep original xhtmlContent in case we need to return it without changes
    originalXhtmlContent = xhtmlContent

    if not originalXhtmlContent or not originalXhtmlContent.strip():
        return originalXhtmlContent

    # if using resolveuid, turn src to real image path
    if 'resolveuid' in xhtmlContent:
        xhtmlContent = ResolveUIDAndCaptionFilter()(xhtmlContent)

    xhtmlContent = "<special_tag>%s</special_tag>" % xhtmlContent
    tree = lxml.html.fromstring(safe_unicode(xhtmlContent))
    imgs = tree.findall('.//img')
    if not imgs:
        return originalXhtmlContent

    portal = api.portal.get()
    portal_url = portal.absolute_url()
    for img in imgs:
        # check if it is a local or an external image
        img_src = img.attrib.get('src', None)
        # wrong <img> without src or external image
        if not img_src or (img_src.startswith('http') and not img_src.startswith(portal_url)):
            continue
        # here, we have an image contained in the portal
        # either absolute path (http://...) or relative (../images/myimage.png)
        imageObj = None
        # absolute path
        if img_src.startswith(portal_url):
            img_src = img_src.replace(portal_url, '')
            try:
                # get the image but remove leading '/'
                imageObj = portal.unrestrictedTraverse(img_src[1:])
            except (KeyError, AttributeError):
                continue
        # relative path
        else:
            try:
                imageObj = context.unrestrictedTraverse(img_src)
            except (KeyError, AttributeError):
                continue
        # maybe we have a ImageScale instead of the real Image object?
        if isinstance(imageObj, ImageScale):
            imageObj = imageObj.aq_inner.aq_parent
        blob_path = None
        # be defensinve in case this is a wrong <img> with a src to someting else than an image...
        if hasattr(aq_base(imageObj), 'getBlobWrapper') and imageObj.get_size():
            blob_path = imageObj.getBlobWrapper().blob._p_blob_committed
        # change img src only if a blob_path was found
        if blob_path:
            img.attrib['src'] = blob_path

    # use encoding to 'ascii' so HTML entities are translated to something readable
    return ''.join([lxml.html.tostring(x,
                                       encoding='ascii',
                                       pretty_print=pretty_print,
                                       method='html') for x in tree.iterchildren()])


def storeImagesLocally(context,
                       xhtmlContent,
                       imagePortalType='Image',
                       store_external_images=True,
                       store_internal_images=True,
                       pretty_print=False,
                       force_resolve_uid=False):
    """If images are found in the given p_xhtmlContent,
       we download it and stored it in p_context, this way we ensure that it will
       always be available in case the external/internal image image disappear.
       If p_store_external_images is True, we retrieve external image and store it
       in p_context, if p_store_internal_images is True, we do the same for internal
       images."""

    def _handle_internal_image(img_src):
        """ """
        # get image from URL
        img_path = img_src.replace(portal_url, '')
        img_path = img_path.lstrip('/')
        img_path = path.join(portal.absolute_url_path(), img_path)

        # right, traverse to image
        try:
            imageObj = portal.unrestrictedTraverse(img_path)
        except KeyError:
            # wrong img_path
            return None, None

        # not an image
        if not imageObj.portal_type == 'Image':
            return None, None

        filename = imageObj.getId()
        data = imageObj.getBlobWrapper().data
        return filename, data

    def _handle_external_image(img_src):
        """ """
        # right, we have an external image, download it, stores it in context and update img_src
        try:
            downloaded_img_path, downloaded_img_infos = urllib.urlretrieve(img_src)
        except IOError:
            # url not existing
            return None, None

        # not an image
        if not downloaded_img_infos.maintype == 'image':
            return None, None

        # retrieve filename
        filename = 'image'
        disposition = downloaded_img_infos.getheader('Content-Disposition')
        # get real filename from 'Content-Disposition' if available
        if disposition:
            disp_value, disp_params = cgi.parse_header(disposition)
            filename = disp_params.get('filename', 'image')
        # if no 'Content-Disposition', at least try to get correct file extension
        elif hasattr(downloaded_img_infos, 'subtype'):
            filename = '{0}.{1}'.format(filename, downloaded_img_infos.subtype)
        f = open(downloaded_img_path, 'r')
        data = f.read()
        f.close()
        # close and delete temporary file
        if path.exists(downloaded_img_path):
            os.remove(downloaded_img_path)
        return filename, data

    tree = _turnToLxmlTree(xhtmlContent)
    if not isinstance(tree, lxml.html.HtmlElement):
        return xhtmlContent

    imgs = tree.findall('.//img')
    if not imgs:
        return xhtmlContent
    portal = api.portal.get()
    portal_url = portal.absolute_url()
    context_url = context.absolute_url()
    # adapter to generate a valid id, it needs a container, so it will be context or it's parent
    try:
        name_chooser = INameChooser(context)
    except TypeError:
        parent = context.getParentNode()
        name_chooser = INameChooser(parent)
    # return received xhtmlContent if nothing was changed
    changed = False
    for img in imgs:
        original_img_src = img.get('src', '')

        # we only handle http stored images
        if not original_img_src.startswith('http') and 'resolveuid' not in original_img_src:
            continue
        filename = data = None
        # external images
        if store_external_images and not original_img_src.startswith(portal_url) and \
           'resolveuid' not in original_img_src:
            filename, data = _handle_external_image(original_img_src)

        # image in portal but not already stored in context
        # handle images using resolveuid
        end_of_url = None
        img_src = original_img_src
        if 'resolveuid' in original_img_src:
            # manage cases like :
            # - resolveuid/2ff7ea3317df43438a09edfa84965b13
            # - resolveuid/2ff7ea3317df43438a09edfa84965b13/image_preview
            # - http://portal_url/resolveuid/2ff7ea3317df43438a09edfa84965b13
            img_uid = original_img_src.split('resolveuid/')[-1].split('/')[0]
            # save end of url if any, like /image_preview
            end_of_url = original_img_src.split(img_uid)[-1]
            if end_of_url == img_uid:
                end_of_url = None
            img_src = uuidToURL(img_uid)

        if store_internal_images and \
           img_src.startswith(portal_url) and \
           not img_src.startswith(context_url):
            filename, data = _handle_internal_image(img_src)

        if not filename:
            continue
        changed = True

        # create image
        name = name_chooser.chooseName(filename, context)
        new_img_id = context.invokeFactory(imagePortalType, id=name, title=name, file=data)
        new_img = getattr(context, new_img_id)
        # store a resolveuid if using it, the absolute_url to image if not
        if force_resolve_uid or \
           original_img_src.startswith('resolveuid') or \
           (HAS_CKEDITOR and
                hasattr(portal.portal_properties, 'ckeditor_properties') and
                portal.portal_properties.ckeditor_properties.allow_link_byuid):
            new_img_src = 'resolveuid/{0}'.format(new_img.UID())
        else:
            new_img_src = new_img.absolute_url()
        if end_of_url:
            new_img_src = '/'.join([new_img_src, end_of_url.strip('/')])

        img.attrib['src'] = new_img_src

    if not changed:
        return xhtmlContent

    return ''.join([lxml.html.tostring(x,
                                       encoding='utf-8',
                                       pretty_print=pretty_print,
                                       method='html') for x in tree.iterchildren()])
