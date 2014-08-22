# -*- coding: utf-8 -*-
import lxml.html


def removeBlanks(xhtmlContent):
    '''This method will remove any blank line in p_xhtmlContent.'''
    if not xhtmlContent or not xhtmlContent.strip():
        return xhtmlContent
    # surround xhtmlContent with a special tag so we are sure that tree is always
    # a list of children of this special tag
    xhtmlContent = "<special_tag>%s</special_tag>" % xhtmlContent
    tree = lxml.html.fromstring(unicode(xhtmlContent, 'utf-8'))
    for el in tree.getchildren():
        if not el.text or el.text.strip() == u'':
            el.getparent().remove(el)
    # only return children of the <special_tag>
    return ''.join([lxml.html.tostring(x, encoding='utf-8') for x in tree.iterchildren()])


def xhtmlContentIsEmpty(xhtmlContent):
    '''This method checks if given p_xhtmlContent will produce someting on rendering.'''
    # first check if xhtmlContent is not simply None or so
    if not xhtmlContent or not xhtmlContent.strip():
        return True

    # surround xhtmlContent with a special tag so we are sure that tree is always
    # a list of children of this special tag
    xhtmlContent = "<special_tag>%s</special_tag>" % xhtmlContent
    import ipdb; ipdb.set_trace()
    tree = lxml.html.fromstring(unicode(xhtmlContent, 'utf-8'))

    for el in tree:
        if not el.text or el.text.strip() == u'':
            el.getparent().remove(el)
    # are there children left?  If not, it means that the field is empty...
    return not bool(tree.getchildren())
