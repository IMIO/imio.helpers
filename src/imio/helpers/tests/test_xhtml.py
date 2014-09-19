# -*- coding: utf-8 -*-

from imio.helpers.testing import IntegrationTestCase
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
