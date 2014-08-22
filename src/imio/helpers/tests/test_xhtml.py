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
        self.assertTrue(removeBlanks('<p>Some text to keep</p><p>&nbsp;</p><i></i>') == '<p>Some text to keep</p>')
        self.assertTrue(removeBlanks('<p> </p><p>Some text to keep</p><p>&nbsp;</p>') == '<p>Some text to keep</p>')
        self.assertTrue(removeBlanks('<p>Text line 1</p><p>Text line 2</p>') == '<p>Text line 1</p><p>Text line 2</p>')

    def test_xhtmlContentIsEmpty(self):
        """
          Test if a given XHTML content will produce someting on render.
        """
        self.assertTrue(xhtmlContentIsEmpty(''))
        self.assertTrue(xhtmlContentIsEmpty(None))
        self.assertTrue(xhtmlContentIsEmpty('<p></p>'))
        self.assertTrue(xhtmlContentIsEmpty('<br><br /><br/>'))
        self.assertTrue(xhtmlContentIsEmpty('<p></p><p>&nbsp;</p><p> </p><b></b><i> </i>'))
        self.assertTrue(not xhtmlContentIsEmpty('<p>Some text to keep</p>'))
        self.assertTrue(not xhtmlContentIsEmpty('<p>&nbsp;</p><p>Some text to keep</p><i>&nbsp;</i>'))
        self.assertTrue(not xhtmlContentIsEmpty('<p>&nbsp;</p><i>Some text to keep</i>'))
