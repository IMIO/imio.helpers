# -*- coding: utf-8 -*-

from Acquisition import aq_base
from html import escape
from imio.helpers import HAS_PLONE_5_AND_MORE
from imio.helpers.utils import create_image_content
from os import path
from plone import api
from plone.outputfilters.browser.resolveuid import uuidToURL
from plone.outputfilters.filters.resolveuid_and_caption import ResolveUIDAndCaptionFilter
from Products.CMFPlone.utils import safe_unicode
from six.moves.html_parser import HTMLParser
from six.moves.urllib.request import urlretrieve
from zExceptions import NotFound
from zope.container.interfaces import INameChooser

import base64
import cgi
import logging
import lxml.html
import os
import pkg_resources
import six


try:
    import pathlib
except ImportError:
    # pathlib batckport for py2.7
    import pathlib2 as pathlib


if HAS_PLONE_5_AND_MORE:
    from plone.namedfile.scaling import ImageScale
else:
    from plone.app.imaging.scale import ImageScale


logger = logging.getLogger('imio.helpers:xhtml')

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
    if six.PY3:
        isStr = isinstance(xhtmlContent, str) or isinstance(xhtmlContent, type(None))
    else:
        isStr = isinstance(xhtmlContent, bytes) or isinstance(xhtmlContent, type(None))
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
        if xhtmlContentIsEmpty(el, tagWithAttributeIsNotEmpty=False):
            el.getparent().remove(el)
    # Will only return children of the <special_tag>
    result = [lxml.html.tostring(x,
                        encoding='ascii',
                        pretty_print=pretty_print,
                        method='html')
              for x in tree.iterchildren()]
    if six.PY3:
        return ''.join([r.decode('utf-8') for r in result])
    return ''.join(result)


def replace_content(xhtml_content,
                    css_class,
                    new_content=u"",
                    new_content_link={},
                    pretty_print=False):
    '''This method will get tags using given p_css_class and
       replace it's content with given p_content.'''
    tree = _turnToLxmlTree(xhtml_content)
    if not isinstance(tree, lxml.html.HtmlElement):
        return xhtml_content

    new_content = safe_unicode(new_content)

    from lxml.cssselect import CSSSelector
    selector = CSSSelector('.' + css_class)
    elements = selector(tree)
    for main_elt in elements:
        # will find every contained elements
        # store itered elements as we add new elements,
        # iteration ignores last elements
        elts = [elt for elt in main_elt.iter()]
        for elt in elts:
            is_main_elt = elt == main_elt
            # make sure elt does not contain sub element
            for sub_elt in elt.getchildren():
                elt.remove(sub_elt)
            if is_main_elt:
                if new_content_link:
                    elt.text = u""
                    new_elt = lxml.html.Element("a")
                    new_elt.attrib["href"] = new_content_link["href"]
                    new_elt.attrib["title"] = new_content_link.get("title", u"")
                    new_elt.text = new_content or u""
                    elt.append(new_elt)
                else:
                    elt.text = new_content or u""
            else:
                elt.tag = "span"
                elt.text = u""
                elt.tail = u""
    if six.PY3:
        result = [lxml.html.tostring(x,
                                       encoding='ascii',
                                       pretty_print=pretty_print,
                                       method='html').decode()
                    for x in tree.iterchildren()]
    else:
        result = [lxml.html.tostring(x,
                                       encoding='ascii',
                                       pretty_print=pretty_print,
                                       method='html')
                    for x in tree.iterchildren()]

    # only return children of the <special_tag>
    return ''.join(result)


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

    if six.PY3:
        result = [lxml.html.tostring(x,
                                      encoding='ascii',
                                      pretty_print=pretty_print,
                                      method='html').decode() for x in children]
    else:
        result = [lxml.html.tostring(x,
                                      encoding='ascii',
                                      pretty_print=pretty_print,
                                      method='html') for x in children]
    # use encoding to 'ascii' so HTML entities are translated to something readable
    res = ''.join(result)
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

    if six.PY3:
        result = [lxml.html.tostring(x,
                                    encoding='ascii',
                                    pretty_print=pretty_print,
                                    method='html').decode() for x in tree.iterchildren()]
    else:
        result = [lxml.html.tostring(x,
                                    encoding='ascii',
                                    pretty_print=pretty_print,
                                    method='html') for x in tree.iterchildren()]
    # use encoding to 'ascii' so HTML entities are translated to something readable
    res = ''.join(result)
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
    if six.PY3:
        result = [lxml.html.tostring(x,
                                    encoding='utf-8',
                                    pretty_print=pretty_print,
                                    method='html').decode() for x in tree.iterchildren()]
    else:
        result = [lxml.html.tostring(x,
                                    encoding='utf-8',
                                    pretty_print=pretty_print,
                                    method='html') for x in tree.iterchildren()]
    return ''.join(result)


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

    if six.PY3:
        result = [lxml.html.tostring(x,
                                    encoding='utf-8',
                                    pretty_print=pretty_print,
                                    method='html').decode() for x in tree.iterchildren()]
    else:
        result = [lxml.html.tostring(x,
                                    encoding='utf-8',
                                    pretty_print=pretty_print,
                                    method='html') for x in tree.iterchildren()]
    return ''.join(result)


def _img_from_src(context, img, portal, portal_url):
    """ """
    # check if it is a local or an external image
    img_src = img.attrib.get('src', None)
    # wrong <img> without src or external image
    if not img_src or (img_src.startswith('http') and not img_src.startswith(portal_url)):
        return
    # here, we have an image contained in the portal
    # either absolute path (http://...) or relative (../images/myimage.png)
    imageObj = None
    # absolute path
    if img_src.startswith(portal_url):
        img_src = img_src.replace(portal_url, '')
        try:
            # get the image but remove leading '/'
            imageObj = portal.unrestrictedTraverse(img_src[1:])
        except (KeyError, AttributeError, NotFound):
            return
    # relative path
    else:
        try:
            imageObj = context.unrestrictedTraverse(img_src)
        # in case we have a wrong resolveuid/unknown_uid, it raises NotFound
        except (KeyError, AttributeError, NotFound):
            return

    # BREAK: XXX ImageScale are not traversable anymore !!!!

    # maybe we have a ImageScale instead of the real Image object?
    if isinstance(imageObj, ImageScale):
        imageObj = imageObj.aq_inner.aq_parent
    return imageObj


def _get_image_blob(imageObj):
    """Be defensinve in case this is a wrong <img> with a src
       to someting else than an image... """
    blob = None
    if HAS_PLONE_5_AND_MORE:
        if hasattr(imageObj, 'image') and imageObj.image and imageObj.get_size():
            blob = imageObj.image
    else:
        img_size = imageObj.get_size()
        if hasattr(aq_base(imageObj), 'getBlobWrapper') and img_size:
            blob = imageObj.getBlobWrapper()
    return blob


def _transform_images(context, xhtmlContent, pretty_print=False, transform_type="path"):
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
        imageObj = _img_from_src(context, img, portal, portal_url)
        if imageObj is None:
            continue

        blob = _get_image_blob(imageObj)
        # change img src only if a blob was found
        blob_path = None
        if blob:
            if transform_type == "path":
                if HAS_PLONE_5_AND_MORE:
                    blob_path = blob._blob._p_blob_committed
                else:
                    blob_path = blob.blob._p_blob_committed
                if blob_path:
                    img.attrib['src'] = blob_path
            elif transform_type == "data":
                # blob_path = blob.blob._p_blob_committed
                # blob_path and
                if HAS_PLONE_5_AND_MORE:
                    blob_content_type = blob.contentType
                    if blob_content_type.startswith('image/'):
                        # py3
                        img.attrib['src'] = "data:{0};base64,{1}".format(
                            blob_content_type, base64.b64encode(blob.data).decode("utf-8"))
                else:
                    blob_content_type = blob.content_type
                    if blob_content_type.startswith('image/'):
                        # py2.7
                        img.attrib['src'] = "data:{0};base64,{1}".format(
                            blob_content_type, base64.b64encode(blob.data))
    if six.PY3:
        result = [lxml.html.tostring(x,
                                       encoding='ascii',
                                       pretty_print=pretty_print,
                                       method='html').decode("utf-8") for x in tree.iterchildren()]
    else:
        result = [lxml.html.tostring(x,
                                       encoding='ascii',
                                       pretty_print=pretty_print,
                                       method='html') for x in tree.iterchildren()]
    # use encoding to 'ascii' so HTML entities are translated to something readable
    return ''.join(result)


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

    return _transform_images(context, xhtmlContent, pretty_print, transform_type="path")


def imagesToData(context, xhtmlContent, pretty_print=False):
    '''Turn <img> source contained in given p_xhtmlContent to a data:image/png;base64... value.
       External images are left unchanged.
       The image_scale is not kept, so we get the full image.'''

    return _transform_images(context, xhtmlContent, pretty_print, transform_type="data")


def storeImagesLocally(context,
                       xhtmlContent,
                       imagePortalType='Image',
                       store_external_images=True,
                       store_internal_images=True,
                       pretty_print=False,
                       force_resolve_uid=False,
                       replace_not_found_image=True):
    """If images are found in the given p_xhtmlContent,
       we download it and stored it in p_context, this way we ensure that it will
       always be available in case the external/internal image image disappear.
       If p_store_external_images is True, we retrieve external image and store it
       in p_context, if p_store_internal_images is True, we do the same for internal
       images.
       If p_replace_not_found_image is True, an image holding text "Image not available"
       will be used if the image could not be retrieved."""

    def _handle_internal_image(img_src):
        """ """
        # get image from URL
        img_path = img_src.replace(portal_url, '')
        img_path = path.join(portal.absolute_url_path(), img_path)
        # path can not start with a '/'
        img_path = img_path.lstrip('/')

        # right, traverse to image
        try:
            imageObj = portal.unrestrictedTraverse(img_path)
        except (KeyError, AttributeError, NotFound):
            # wrong img_path
            logger.warning(
                'In \'storeImagesLocally\', could not traverse '
                'img_path \'{0}\' for \'{1}\'!'.format(
                    img_path, context.absolute_url()))
            return None, None

        # not an image
        if getattr(imageObj, 'portal_type', None) != 'Image':
            return None, None

        filename = imageObj.getId()
        if HAS_PLONE_5_AND_MORE:
            data = imageObj.image.data
        else:
            # In Plone4 python 2.x : imageObj is <ATImage at /plone/dot.gif>
            data = imageObj.getBlobWrapper().data
        return filename, data

    def _handle_external_image(img_src):
        """ """
        # right, we have an external image, download it, stores it in context and update img_src
        try:
            downloaded_img_path, downloaded_img_infos = urlretrieve(img_src)
        except (IOError, UnicodeError):
            # url not existing
            return None, None

        # BREAK : with base64 image, downloaded_img_infos is <email.message.Message object at 0x7f4e1e3b25f0> !!!

        # not an image
        if six.PY3:
            if not downloaded_img_infos.get_content_type().split('/')[0] == 'image':
                return None, None
        else:
            if not downloaded_img_infos.maintype == 'image':
                return None, None

        # retrieve filename
        filename = None
        if six.PY3:
            disposition = downloaded_img_infos.get_content_disposition()
        else:
            disposition = downloaded_img_infos.getheader('Content-Disposition')
        if hasattr(downloaded_img_infos, 'get_filename'):
            filename = downloaded_img_infos.get_filename()
        # get real filename from 'Content-Disposition' if available
        if not filename and disposition:
            disp_value, disp_params = cgi.parse_header(disposition)
            filename = disp_params.get('filename', 'image')
        if not filename:
            filename = 'image'
        # if no extension, at least try to get correct file extension
        if not pathlib.Path(filename).suffix and getattr(downloaded_img_infos, 'subtype', None):
            filename = '{0}.{1}'.format(filename, downloaded_img_infos.subtype)
        f = open(downloaded_img_path, 'rb')
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
    # make sure context_url ends with a '/' to avoid mismatch if folder holding the
    # image absolute_url starts with context_url
    context_url = context.absolute_url() + '/'
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
        if not original_img_src.startswith('http') and \
           'resolveuid' not in original_img_src and \
           ';base64,' not in original_img_src:
            continue
        filename = data = None
        handled = False
        # external images
        if store_external_images and not original_img_src.startswith(portal_url) and \
           'resolveuid' not in original_img_src:
            filename, data = _handle_external_image(original_img_src)
            handled = True

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
            # if not found, like when copy/paste HTML code containing resolveuid, use '' instead None
            img_src = uuidToURL(img_uid) or ''

        if store_internal_images and \
           img_src.startswith(portal_url) and \
           not img_src.startswith(context_url):
            filename, data = _handle_internal_image(img_src)
            handled = True

        if not filename:
            if handled:
                if replace_not_found_image:
                    filename = "imageNotFound.jpg"
                    f = open(os.path.join(os.path.dirname(__file__), filename), 'r')
                    data = f.read()
                    f.close()
                else:
                    continue
            else:
                continue

        changed = True

        # create image
        name = name_chooser.chooseName(filename, context)
        new_img = create_image_content(
            container=context,
            title=name,
            id=name,
            filename=name,
            portal_type=imagePortalType,
            data=data,
        )

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
    if six.PY3:
        result = [lxml.html.tostring(x,
                                    encoding='utf-8',
                                    pretty_print=pretty_print,
                                    method='html').decode() for x in tree.iterchildren()]
    else:
        result = [lxml.html.tostring(x,
                                    encoding='utf-8',
                                    pretty_print=pretty_print,
                                    method='html') for x in tree.iterchildren()]
    return ''.join(result)


def separate_images(xhtmlContent, pretty_print=False):
    """Make sure images are separated in different paragraphs.
       So <p><img .../><img .../></p> is changed to
       <p><img .../></p></p><img .../></p>."""

    tree = _turnToLxmlTree(xhtmlContent)
    # bypass if wrong format or no img
    if not isinstance(tree, lxml.html.HtmlElement) or \
       not tree.xpath('.//img'):
        return xhtmlContent

    # return received xhtmlContent if nothing was changed
    changed = False
    inserted_index = 1
    for elt_index, elt in enumerate(tree.getchildren()):
        if elt.tag not in ('p', 'div'):
            continue
        # only manage <p>/<div> containing several <img>, nothing else
        imgs = elt.xpath('.//img')
        len_imgs = len(imgs)
        if len_imgs > 1:
            # <p> may not contain anything else than <img> or <br>
            contained_tags = [child for child in elt.getchildren()
                              if child.tag not in ('br', )]
            # contained text, if <p> contains <img> and text, we can not separate it
            if len_imgs == len(contained_tags) and not elt.text_content().strip():
                changed = True
                for img_index, img in enumerate(imgs[1:]):
                    new_elt = lxml.html.Element(elt.tag)
                    tree.insert(elt_index + inserted_index + img_index, new_elt)
                    inserted_index += 1
                    # append will move the img, not necessary to remove from elt
                    new_elt.append(img)

    if not changed:
        return xhtmlContent

    if six.PY3:
        result = [lxml.html.tostring(x,
                                    encoding='utf-8',
                                    pretty_print=pretty_print,
                                    method='html').decode() for x in tree.iterchildren()]
    else:
        result = [lxml.html.tostring(x,
                                    encoding='utf-8',
                                    pretty_print=pretty_print,
                                    method='html') for x in tree.iterchildren()]
    return ''.join(result)


def object_link(obj, view='view', attribute='Title', content='', target='', escaped=True):
    """ Returns an html link for the given object """
    href = view and "%s/%s" % (obj.absolute_url(), view) or obj.absolute_url()
    if not content:
        if not hasattr(obj, attribute):
            attribute = 'Title'
        content = getattr(obj, attribute)
        if callable(content):
            content = content()
    if target:
        target = ' target="{}"'.format(target)
    if escaped:
        content = escape(content)
    return u'<a href="%s"%s>%s</a>' % (href, target, safe_unicode(content))


def is_html(text):
    """Check that given p_text is HTML."""
    text = text or ''
    mtr = api.portal.get_tool('mimetypes_registry')
    # taken from Products.Archetypes/Field.py
    try:
        d, f, mimetype = mtr(text[:8096], mimetype=None)
    except UnicodeDecodeError:
        d, f, mimetype = mtr(len(text) < 8096 and text or '', mimetype=None)
    return str(mimetype).split(';')[0].strip() == 'text/html'


def unescape_html(html):
    """Unescape an html text, turn HTML entities to encoded entities."""
    if not html:
        return html
    is_unicode = isinstance(html, six.text_type)
    parser = HTMLParser()
    if hasattr(parser, 'unescape'):
        html = parser.unescape(html)
    elif six.PY3:
        import html as htmllib
        html = htmllib.unescape(html)
    return html if is_unicode else html.encode('utf-8')
