# -*- coding: utf-8 -*-
import lxml.html
import types
from Products.CMFPlone.utils import safe_unicode


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


def removeBlanks(xhtmlContent):
    '''This method will remove any blank line in p_xhtmlContent.'''
    if not xhtmlContent or not xhtmlContent.strip():
        return xhtmlContent
    # surround xhtmlContent with a special tag so we are sure that tree is always
    # a list of children of this special tag
    xhtmlContent = "<special_tag>%s</special_tag>" % xhtmlContent
    tree = lxml.html.fromstring(safe_unicode(xhtmlContent))
    for el in tree.getchildren():
        # el can be a subtree, like <ul><li>...</li></ul> we must consider entire rendering of it
        if xhtmlContentIsEmpty(el):
            el.getparent().remove(el)
    # only return children of the <special_tag>
    return ''.join([lxml.html.tostring(x, encoding='utf-8', pretty_print=True, method='xml')
                    for x in tree.iterchildren()])


def addClassToLastChildren(xhtmlContent,
                           classNames={'p': 'pmParaKeepWithNext',
                                       'div': 'pmParaKeepWithNext',
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
                                       'ul': '',
                                       'li': 'podItemKeepWithNext'},
                           numberOfChars=60):
    '''This method will add a class attribute adding class correspondig to tag given in p_classNames
       to the last tags of given p_xhtmlContent.
       It only consider given p_classNames keys which are text formatting tags and will define the class
       on last tags until it contains given p_numberOfChars number of characters.
    '''
    if not xhtmlContent or not xhtmlContent.strip():
        return xhtmlContent

    # surround xhtmlContent with a special tag so we are sure that tree is always
    # a list of children of this special tag
    tree = lxml.html.fromstring(safe_unicode("<special_tag>%s</special_tag>" % xhtmlContent.strip()))
    children = tree.getchildren()
    if not children:
        return xhtmlContent

    tags = classNames.keys()

    def adaptTree(children, managedNumberOfChars=0):
        """
          Recursive method that walk the children and subchildren and adapt what necessary.
        """
        # apply style on last element until we reached necessary numberOfChars or we encounter
        # a tag not in p_tags or we do not have a tag...
        i = 1
        stillNeedToAdaptPreviousChild = True
        numberOfChildren = len(children)
        while stillNeedToAdaptPreviousChild and i <= numberOfChildren:
            child = children[-i]
            if not child.tag in tags and not child.getchildren():
                stillNeedToAdaptPreviousChild = False
            else:
                # check if tag did not already have a class attribute
                # in this case, we append classNames[child.tag] to existing classes
                # and only if there is a classNames[child.tag]
                cssClass = classNames.get(child.tag, '')
                if 'class' in child.attrib:
                    cssClass = '{0} {1}'.format(cssClass, child.attrib['class'])
                if cssClass:
                    child.attrib['class'] = cssClass
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
                                      pretty_print=True,
                                      method='xml') for x in tree.iterchildren()])
    return res


def markEmptyTags(xhtmlContent, markingClass='highlightBlankRow', tagTitle='', onlyAtTheEnd=False, tags=('p', 'div', )):
    '''This will add a CSS class p_markingClass to tags of the given p_xhtmlContent
       that are empty.  If p_onlyAtTheEnd is True, it will only mark empty rows that are
       ending the XHTML content.'''
    if not xhtmlContent or not xhtmlContent.strip():
        return xhtmlContent

    # surround xhtmlContent with a special tag so we are sure that tree is always
    # a list of children of this special tag
    xhtmlContent = "<special_tag>%s</special_tag>" % xhtmlContent
    tree = lxml.html.fromstring(safe_unicode(xhtmlContent))
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
    return ''.join([lxml.html.tostring(x, encoding='utf-8', pretty_print=True, method='xml')
                    for x in tree.iterchildren()])
