# -*- coding: utf-8 -*-

from imio.helpers.testing import IntegrationTestCase
from imio.helpers.xhtml import addClassToLastChildren
from imio.helpers.xhtml import removeBlanks
from imio.helpers.xhtml import xhtmlContentIsEmpty


class TestXHTMLModule(IntegrationTestCase):
    """
    Test all helper methods of xhtml module.
    """

    def test_removeBlanks(self):
        """
        Normal usecase of removeBlanks, this will remove
        every blank lines of a given XHTML content.
        """
        self.assertTrue(removeBlanks('') == '')
        self.assertTrue(removeBlanks(None) is None)
        self.assertTrue(removeBlanks('<p></p>') == '')
        self.assertTrue(removeBlanks('<p></p><br><br /><br/>') == '')
        self.assertTrue(removeBlanks('<p>&nbsp;</p>') == '')
        self.assertTrue(removeBlanks('<p>&nbsp;<p><p>&nbsp;</p><i></i>') == '')
        self.assertTrue(removeBlanks('<p>Some text to keep</p><p>&nbsp;</p><i></i>') ==
                        '<p>Some text to keep</p>\n')
        self.assertTrue(removeBlanks('<p> </p><p>Some text to keep</p><p>&nbsp;</p>') ==
                        '<p>Some text to keep</p>\n')
        self.assertTrue(removeBlanks('<p>Text line 1</p><p>Text line 2</p>') ==
                        '<p>Text line 1</p>\n<p>Text line 2</p>\n')
        self.assertTrue(removeBlanks('<p><img src="my_image"/></p>') ==
                        '<p>\n  <img src="my_image"/>\n</p>\n')
        # complex tree filled
        self.assertTrue(removeBlanks('<ul><li>First line</li><li>second line</li></ul>') ==
                        '<ul>\n  <li>First line</li>\n  <li>second line</li>\n</ul>\n')
        # complex tree semi-filled
        self.assertTrue(removeBlanks('<ul><li>First line</li><li></li></ul>') ==
                        '<ul>\n  <li>First line</li>\n  <li/>\n</ul>\n')
        # empty complex tree, is not wiped out because master tag containing children
        self.assertTrue(removeBlanks('<ul><li></li><li></li></ul>') ==
                        '<ul>\n  <li/>\n  <li/>\n</ul>\n')

    def test_xhtmlContentIsEmpty(self):
        """
          Test if a given XHTML content will produce someting on render.
        """
        self.assertTrue(xhtmlContentIsEmpty(''))
        self.assertTrue(xhtmlContentIsEmpty(None))
        self.assertTrue(xhtmlContentIsEmpty('<p></p>'))
        self.assertTrue(xhtmlContentIsEmpty('<br/><br/><br/>'))
        self.assertTrue(xhtmlContentIsEmpty('<p></p><p>&nbsp;</p><p> </p><b></b><i> </i>'))
        self.assertTrue(xhtmlContentIsEmpty('<img />'))
        # empty <p> with an attribute, considered not empty
        self.assertTrue(not xhtmlContentIsEmpty('<p class="special_empty_line"></p>'))
        # tree with children, considered not empty
        self.assertTrue(not xhtmlContentIsEmpty('<table><tr><td> </td><td>&nbsp;</td></tr></table>'))
        self.assertTrue(not xhtmlContentIsEmpty("Some text without any tag"))
        self.assertTrue(not xhtmlContentIsEmpty("<p>Some broken HTML<broken_tag>text<broken_tag> </i></div>"))
        self.assertTrue(not xhtmlContentIsEmpty('<p>Some text to keep</p>'))
        self.assertTrue(not xhtmlContentIsEmpty('<p>&nbsp;</p><p>Some text to keep</p><i>&nbsp;</i>'))
        self.assertTrue(not xhtmlContentIsEmpty('<p>&nbsp;</p><i>Some text to keep</i>'))
        self.assertTrue(not xhtmlContentIsEmpty('<table><tr><td>Some text to keep</td><td>&nbsp;</td></tr></table>'))
        self.assertTrue(not xhtmlContentIsEmpty('<p><img src="my_image_path.png"/></p>'))

    def test_addClassToLastChildren(self):
        """
          Test if adding a class to last x tags of a given XHTML content works.
          By default, this method receives following parameters :
          - xhtmlContent;
          - className={'p': 'paraKeepWithNext',
                       'li': 'itemKeepWithNext'};
          - tags=('p', 'li', );
          - numberOfChars=60.
        """
        self.assertTrue(addClassToLastChildren('') == '')
        self.assertTrue(addClassToLastChildren(None) is None)
        self.assertTrue(addClassToLastChildren('text') == 'text')
        # if tag is not handled, it does not change anything, by default, tags 'p' and 'li' are handled
        self.assertTrue(addClassToLastChildren('<span>My text with tag not handled</span>') ==
                        '<span>My text with tag not handled</span>\n')
        # now test with a single small handled tag, text size is lower than numberOfChars
        self.assertTrue(addClassToLastChildren('<p>My small text</p>') ==
                        '<p class="paraKeepWithNext">My small text</p>\n')
        # existing class attribute is kept
        self.assertTrue(addClassToLastChildren('<p class="myclass">My small text</p>') ==
                        '<p class="paraKeepWithNext myclass">My small text</p>\n')
        # test that if text is smaller than numberOfChars, several last tags are adapted
        self.assertTrue(addClassToLastChildren('<p>My small text</p><p>My small text</p>') ==
                        '<p class="paraKeepWithNext">My small text</p>\n'
                        '<p class="paraKeepWithNext">My small text</p>\n')
        # large text, only relevant tags are adapted until numberOfChars is rechead
        self.assertTrue(addClassToLastChildren('<p>13 chars line</p>'
                                               '<p>33 characters text line text line</p>'
                                               '<p>33 characters text line text line</p>') ==
                        '<p>13 chars line</p>\n<p class="paraKeepWithNext">33 characters text line text line</p>\n'
                        '<p class="paraKeepWithNext">33 characters text line text line</p>\n')
        # test mixing different handled tags like 'li' and 'p'
        self.assertTrue(addClassToLastChildren('<p>13 chars line</p><ul><li>Line 1</li><li>Line 2</li>'
                                               '<li>33 characters text line text line</li></ul>'
                                               '<p>33 characters text line text line</p>') ==
                        '<p>13 chars line</p>\n<ul>\n  <li>Line 1</li>\n  <li>Line 2</li>\n  '
                        '<li class="paraKeepWithNext">33 characters text line text line</li>\n</ul>\n'
                        '<p class="paraKeepWithNext">33 characters text line text line</p>\n')
        # as soon as an unhandled tag is discover, adaptation stops
        self.assertTrue(addClassToLastChildren('<p>13 chars line</p>'
                                               '<img src="image.png"/>'
                                               '<p>13 chars line</p>') ==
                        '<p>13 chars line</p>\n'
                        '<img src="image.png"/>\n'
                        '<p class="paraKeepWithNext">13 chars line</p>\n')
