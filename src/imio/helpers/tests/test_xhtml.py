# -*- coding: utf-8 -*-

from imio.helpers.testing import IntegrationTestCase
from imio.helpers.xhtml import addClassToLastChildren
from imio.helpers.xhtml import markEmptyTags
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
        self.assertTrue(not xhtmlContentIsEmpty('<p><ul><li> </li><li>&nbsp;</li></ul></p>'))
        # tree with some kind of children are considered empty
        self.assertTrue(xhtmlContentIsEmpty('<p><br /></p>'))
        self.assertTrue(xhtmlContentIsEmpty('<p><br /><br /></p>'))
        self.assertTrue(xhtmlContentIsEmpty('<p>&nbsp;<br /></p>'))
        self.assertTrue(xhtmlContentIsEmpty('<p></p>\n\n'))
        self.assertTrue(xhtmlContentIsEmpty('<p><br />\n&nbsp;</p>\n'))

        # other content
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
          - classNames={'p': 'pmParaKeepWithNext',
                       'li': 'podItemKeepWithNext'};
          - tags=('p', 'li', );
          - numberOfChars=60.
        """
        self.assertTrue(addClassToLastChildren('') == '')
        self.assertTrue(addClassToLastChildren(None) is None)
        self.assertTrue(addClassToLastChildren('text') == 'text')
        # if tag is not handled, it does not change anything, by default, tags 'p' and 'li' are handled
        self.assertTrue(addClassToLastChildren('<unhandled_tag>My text with tag not handled</unhandled_tag>') ==
                        '<unhandled_tag>My text with tag not handled</unhandled_tag>\n')
        # now test with a single small handled tag, text size is lower than numberOfChars
        self.assertTrue(addClassToLastChildren('<p>My small text</p>') ==
                        '<p class="pmParaKeepWithNext">My small text</p>\n')
        # existing class attribute is kept
        self.assertTrue(addClassToLastChildren('<p class="myclass">My small text</p>') ==
                        '<p class="pmParaKeepWithNext myclass">My small text</p>\n')
        # test that if text is smaller than numberOfChars, several last tags are adapted
        self.assertTrue(addClassToLastChildren('<p>My small text</p><p>My small text</p>') ==
                        '<p class="pmParaKeepWithNext">My small text</p>\n'
                        '<p class="pmParaKeepWithNext">My small text</p>\n')
        # large text, only relevant tags are adapted until numberOfChars is rechead
        self.assertTrue(addClassToLastChildren('<p>13 chars line</p>'
                                               '<p>33 characters text line text line</p>'
                                               '<p>33 characters text line text line</p>') ==
                        '<p>13 chars line</p>\n<p class="pmParaKeepWithNext">33 characters text line text line</p>\n'
                        '<p class="pmParaKeepWithNext">33 characters text line text line</p>\n')
        # tags with children
        self.assertTrue(addClassToLastChildren('<p>First untouched paragraph</p>'
                                               '<p><strong>Strong text Strong text Strong text Strong text</strong> '
                                               'Paragraph text Paragraph text Paragraph text</p>') ==
                        '<p>First untouched paragraph</p>\n'
                        '<p class="pmParaKeepWithNext"><strong>Strong text Strong text Strong '
                        'text Strong text</strong> Paragraph text Paragraph text Paragraph text</p>\n')

        # test mixing different handled tags like 'li' and 'p'
        self.assertTrue(addClassToLastChildren('<p>13 chars line</p><ul><li>Line 1</li><li>Line 2</li>'
                                               '<li>33 characters text line text line</li></ul>'
                                               '<p>33 characters text line text line</p>') ==
                        '<p>13 chars line</p>\n<ul>\n  <li>Line 1</li>\n  <li>Line 2</li>\n  '
                        '<li class="podItemKeepWithNext">33 characters text line text line</li>\n</ul>\n'
                        '<p class="pmParaKeepWithNext">33 characters text line text line</p>\n')
        # as soon as an unhandled tag is discover, adaptation stops
        self.assertTrue(addClassToLastChildren('<p>13 chars line</p>'
                                               '<img src="image.png"/>'
                                               '<p>13 chars line</p>') ==
                        '<p>13 chars line</p>\n'
                        '<img src="image.png"/>\n'
                        '<p class="pmParaKeepWithNext">13 chars line</p>\n')
        # test with sub tags
        self.assertTrue(addClassToLastChildren('<p>Text</p><p><u><strong>dsdklm</strong></u></p>') ==
                        '<p class="pmParaKeepWithNext">Text</p>\n'
                        '<p class="pmParaKeepWithNext">\n  '
                        '<u>\n    '
                        '<strong>dsdklm</strong>\n  '
                        '</u>\n</p>\n')
        # test every available tags
        self.assertTrue(addClassToLastChildren('<p>Text</p>'
                                               '<p><strong>Strong</strong></p>'
                                               '<p><span>Span</span></strong>'
                                               '<p><strike>Strike</strike></p>'
                                               '<p><i>I</i></p>'
                                               '<p><em>Em</em></p>'
                                               '<p><u>U</u></p>'
                                               '<p><small>Small</small></p>'
                                               '<p><mark>Mark</mark></p>'
                                               '<p><del>Del</del></p>'
                                               '<p><ins>Ins</ins></p>'
                                               '<p><sub>Sub</sub></p>'
                                               '<p><sup>Sup</sup></p>',
                                               numberOfChars=85) ==
                        '<p class="pmParaKeepWithNext">Text</p>\n'
                        '<p class="pmParaKeepWithNext">\n  <strong>Strong</strong>\n</p>\n'
                        '<p class="pmParaKeepWithNext">\n  <span>Span</span>\n</p>\n'
                        '<p class="pmParaKeepWithNext">\n  <strike>Strike</strike>\n</p>\n'
                        '<p class="pmParaKeepWithNext">\n  <i>I</i>\n</p>\n'
                        '<p class="pmParaKeepWithNext">\n  <em>Em</em>\n</p>\n'
                        '<p class="pmParaKeepWithNext">\n  <u>U</u>\n</p>\n'
                        '<p class="pmParaKeepWithNext">\n  <small>Small</small>\n</p>\n'
                        '<p class="pmParaKeepWithNext">\n  <mark>Mark</mark>\n</p>\n'
                        '<p class="pmParaKeepWithNext">\n  <del>Del</del>\n</p>\n'
                        '<p class="pmParaKeepWithNext">\n  <ins>Ins</ins>\n</p>\n'
                        '<p class="pmParaKeepWithNext">\n  <sub>Sub</sub>\n</p>\n'
                        '<p class="pmParaKeepWithNext">\n  <sup>Sup</sup>\n</p>\n')
        # does not break with unknown sub tags
        self.assertTrue(addClassToLastChildren('<p><unknown><tagtag>Text</tagtag></unknown></p>') ==
                        '<p class="pmParaKeepWithNext">\n  '
                        '<unknown>\n    '
                        '<tagtag>Text</tagtag>\n  '
                        '</unknown>\n</p>\n')
        # special characters are transformed to HTML entities
        text = "<p>Some spécial charaçters &eacute;</p><p>&nbsp;</p>"
        self.assertTrue(addClassToLastChildren(text) ==
                        '<p class="pmParaKeepWithNext">Some sp&#233;cial chara&#231;ters &#233;</p>\n'
                        '<p class="pmParaKeepWithNext">&#160;</p>\n')

    def test_markEmptyTags(self):
        """
          Test if empty tags are correctly marked with a CSS class.
          markEmptyTags can receive different parameters :
          - markingClass : the class that will mark the empty tags;
          - tagTitle : if given, a 'title' attribute is added to the marked tags;
          - onlyAtTheEnd : if True, only empty tags at the end of the XHTML content are marked;
          - tags : a list of handled tags.
        """
        self.assertTrue(markEmptyTags('') == '')
        self.assertTrue(markEmptyTags(None) is None)
        self.assertTrue(markEmptyTags("<p></p>") == '<p class="highlightBlankRow"/>\n')
        self.assertTrue(markEmptyTags("<p> </p>") == '<p class="highlightBlankRow"> </p>\n')
        self.assertTrue(markEmptyTags("<p>Text</p>") == '<p>Text</p>\n')
        self.assertTrue(markEmptyTags("<p>Text</p><p></p>") == '<p>Text</p>\n<p class="highlightBlankRow"/>\n')
        # change markingClass
        self.assertTrue(markEmptyTags("<p> </p>", markingClass='customClass') == '<p class="customClass"> </p>\n')
        # "span" not handled by default
        self.assertTrue(markEmptyTags("<span></span>") == '<span/>\n')
        # but "span" could be handled if necessary
        self.assertTrue(markEmptyTags("<span></span>", tags=('span', )) == '<span class="highlightBlankRow"/>\n')
        # by default every empty tags are highlighted, but we can specify to highlight only trailing
        # ones aka only tags ending the XHTML content
        self.assertTrue(markEmptyTags("<p></p><p>Text</p><p></p>") ==
                        '<p class="highlightBlankRow"/>\n<p>Text</p>\n<p class="highlightBlankRow"/>\n')
        self.assertTrue(markEmptyTags("<p></p><p>Text</p><p></p>", onlyAtTheEnd=True) ==
                        '<p/>\n<p>Text</p>\n<p class="highlightBlankRow"/>\n')
        # we can also specify to add a title attribute to the highlighted tags
        self.assertTrue(markEmptyTags("<p>Text</p><p></p>", tagTitle='My tag title') ==
                        '<p>Text</p>\n<p class="highlightBlankRow" title="My tag title"/>\n')
        # if an empty tag already have a class, the marking class is appended to it
        self.assertTrue(markEmptyTags("<p class='existingClass'></p>") ==
                        '<p class="highlightBlankRow existingClass"/>\n')

        # we may mark Unicode as well as UTF-8 xhtmlContent
        self.assertEquals(markEmptyTags('<p>UTF-8 string with special chars: \xc3\xa9</p>'),
                          '<p>UTF-8 string with special chars: \xc3\xa9</p>\n')
        self.assertEquals(markEmptyTags(u'<p>Unicode string with special chars: \xe9</p>'),
                          '<p>Unicode string with special chars: \xc3\xa9</p>\n')
