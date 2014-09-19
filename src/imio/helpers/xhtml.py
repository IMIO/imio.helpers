# -*- coding: utf-8 -*-
import lxml.html
import types


def xhtmlContentIsEmpty(xhtmlContent):
    '''This method checks if given p_xhtmlContent will produce someting on rendering.
       p_xhtmlContent can either be a string or already a lxml.html element.'''
    # first check if xhtmlContent is not simply None or so
    isStr = isinstance(xhtmlContent, types.StringType) or isinstance(xhtmlContent, types.NoneType)
    if isStr and (not xhtmlContent or not xhtmlContent.strip()):
        return True

    if isStr:
        xhtmlContent = "<special_tag>%s</special_tag>" % xhtmlContent
        tree = lxml.html.fromstring(unicode(xhtmlContent, 'utf-8'))
    else:
        tree = xhtmlContent
    if tree.tag == 'special_tag':
        if tree.getchildren():
            for el in tree.getchildren():
                if bool(el.text_content().strip()) or bool(el.attrib) or bool(el.getchildren()):
                    return False
            return True

    # if xhtmlContent renders text or has attributes or has children, we consider it not empty
    return not bool(tree.text_content().strip()) and not bool(tree.attrib) and not bool(tree.getchildren())


def removeBlanks(xhtmlContent):
    '''This method will remove any blank line in p_xhtmlContent.'''
    if not xhtmlContent or not xhtmlContent.strip():
        return xhtmlContent
    # surround xhtmlContent with a special tag so we are sure that tree is always
    # a list of children of this special tag
    xhtmlContent = "<special_tag>%s</special_tag>" % xhtmlContent
    tree = lxml.html.fromstring(unicode(xhtmlContent, 'utf-8'))
    for el in tree.getchildren():
        # el can be a subtree, like <ul><li>...</li></ul> we must consider entire rendering of it
        if xhtmlContentIsEmpty(el):
            el.getparent().remove(el)
    # only return children of the <special_tag>
    return ''.join([lxml.html.tostring(x, encoding='utf-8', pretty_print=True, method='xml') for x in tree.iterchildren()])
