# -*- coding: utf-8 -*-

from imio.helpers import HAS_PLONE_5_AND_MORE
from imio.helpers import PLONE_MAJOR_VERSION
from imio.helpers.testing import FUNCTIONAL
from imio.helpers.testing import IntegrationTestCase
from imio.helpers.tests.utils import get_file_data
from imio.helpers.tests.utils import require_module
from imio.helpers.utils import create_image_content
from imio.helpers.xhtml import addClassToContent
from imio.helpers.xhtml import addClassToLastChildren
from imio.helpers.xhtml import imagesToData
from imio.helpers.xhtml import imagesToPath
from imio.helpers.xhtml import is_html
from imio.helpers.xhtml import markEmptyTags
from imio.helpers.xhtml import object_link
from imio.helpers.xhtml import removeBlanks
from imio.helpers.xhtml import removeCssClasses
from imio.helpers.xhtml import replace_content
from imio.helpers.xhtml import separate_images
from imio.helpers.xhtml import storeImagesLocally
from imio.helpers.xhtml import unescape_html
from imio.helpers.xhtml import xhtmlContentIsEmpty

import os
import six
import transaction


try:
    from Products.ATContentTypes.interfaces import IImageContent
except ImportError:
    print("require Archetypes")


picsum_image1_url = 'https://fastly.picsum.photos/id/10/200/300.jpg?hmac=94QiqvBcKJMHpneU69KYg2pky8aZ6iBzKrAuhSUBB9s'
picsum_image2_url = 'https://fastly.picsum.photos/id/1082/200/200.jpg?hmac=3usO1ziO7kCseIG52ruhRigxyk39W_L9eECWe1Hs6fY'

base64_img_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAADWElEQVQ4ja2VX2yTBRTFj2QP" \
    "JGtoLWWMZWN/tDBW1oQSoatuUNycNnWYMV1M9nVrJgRit6msVWuBj5fhQkhB5jagIqDQP2MmkKyDbToSKjSAo2yYInUhuiFEohghcQH7HR9M" \
    "2RLWgJGTnJf7cJOb87v3AlOUk4OZGg1WlRqxztEE7/p6fL5hLbwf2dHneAfBTQ58k5YGLR5Hi56Fzirgs9JVaC41wpKdDV12NnQZGchXKpGp" \
    "UiFDqcSsx2pWWIgS4wo4i4vw2pTyU//Bk1IqMcv0ElyaBVgGACrVMrNW6zy9dGlL9FHWaj/sTfQRRcwAAOifQ2XVajgBQC6fn1dWtu+ezXaM" \
    "jY3J3bryXYqrW2gRPDEAeL1sbkW7Xd0BYAbW1+PT/HwYACAzc2XNzZt/SiQpSZO+e/ceJUkiSf7V18vfKwp5/9yLHBqKxgBgZ1NWx6gvj29X" \
    "Zb4Fswmu+ekoAICsrCUlodA1qbY2QEHwUxD8bG7uYSh0jVu3DrCuLkCL4OflU3l0OWZy48aOW6mpqemly59+QVyb6wIAvLkGO9LTUfBMRoph" \
    "sVpWaahuH9UXtbOg4gsWGHfdCgSG452dPSM225d3gsEIvd4wi5aX31arC6MajfXgQwkbV2CdWo2S1kb5xW8PzKNz9xoaWnZQ726jektXbHj4" \
    "BjWa4vITJ777u7//Kq9c+ZVO587o87qFb5Qs0VQ8IGWBPA8AIJMhTfwAR7/aPnvstEfFru1zWNvpYGrbWabUu0+eDV+9bjJVWY8cCU6EQhFe" \
    "uDDCzQ3O34LtjfRsssYUCoXik/dydw0fXHRDr5XrIJMhbcv76D7unv3z+UNzGPbmsHu/lrq2A0ypd58c+Pr762ZztbW7u3/i8OFBejx93Ptx" \
    "a/KGiZH3i4qhvYdelsz73JLQtpkLd3cxVzwei0R+oU5XXD4+Ph4fHBzl2Ngf9Pl8yUeeGsq8xepKfXXnj0WGyVC83kvxPXuCI9u2Be5EIlGe" \
    "OXORpldeTR7KdNjU1QVosfhpsfhpt/cwHP6JojjAmhovhRofL5/KTY7NdGBPhToBdjz+L9gTfb28/QDsHx4Ge5rVu2+zHWNDQ3InVk+YbvWe" \
    "+HEAkp6v/6cnemATSvoCmtFvb0Kvy47BR72AfwDXsx4tZedcTQAAAABJRU5ErkJggg=="

base64_gif_img_data = "data:image/gif;base64,R0lGODlhCgAKAPcAAP////79/f36+/3z8/zy8/rq7Prm6Pnq7Pje4vTx8v" \
    "Pg5O6gqe2gqOq4v+igqt9tetxSYNs7Tdo5TNc5TNUbMdUbMNQRKNIKIdIJINIGHdEGHtEDGtACFdAAFtAAFNAAEs8AFAAAAAAAA" \
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" \
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" \
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" \
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" \
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" \
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAACIAIP3sAAoACBL2OAAAAPjHWRQAABUKiAAAABL2FAAAAhL+dPkBhPm4MP///xL2YPZNegA" \
    "AAAAQAAAABgAAAAAAABL2wAAAAAAARRL25PEPfxQAAPEQAAAAAAAAA/3r+AAAAAAAGAAAABL2uAAAQgAAABL2pAAAAAAAAAAAAAA" \
    "ADAAAAgABAfDTAAAAmAAAAAAAAAAAABL27Mku0AAQAAAAAAAAAEc1MUaDsAAAGBL3FPELyQAAAAABEgAAAwAAAQAAAxL22AAAmB" \
    "L+dPO4dPPKQP///0c70EUoOQAAmMku0AAQABL3TAAAAEaDsEc1MUaDsAAABkT98AABEhL3wAAALAAAQAAAQBL3kQAACSH5BAEAA" \
    "AAALAAAAAAKAAoAQAhGAAEIHEhw4IIIFCAsKCBwQAQQFyKCeKDAIEKFDAE4hBiRA0WCAwwUBLCAA4cMICg0YIjAQoaIFzJMSCCw" \
    "5EkOKjM2FDkwIAA7"


class TestXHTMLModule(IntegrationTestCase):
    """
    Test all helper methods of xhtml module.
    """

    layer = FUNCTIONAL

    def test_removeBlanks(self):
        """
        Normal usecase of removeBlanks, this will remove
        every blank lines of a given XHTML content.
        """
        self.assertEqual(removeBlanks(''), '')
        self.assertEqual(removeBlanks(None), None)
        self.assertEqual(removeBlanks('<p></p>'), '')
        self.assertEqual(removeBlanks('<p></p><br><br /><br/>'), '')
        self.assertEqual(removeBlanks('<p>&nbsp;</p>'), '')
        self.assertEqual(removeBlanks('<p>&nbsp;<p><p>&nbsp;</p><i></i>'), '')
        self.assertEqual(removeBlanks('<p>Some text to keep</p><p>&nbsp;</p><i>&nbsp;</i>'),
                         '<p>Some text to keep</p>')
        self.assertEqual(removeBlanks('<p> </p><p>Some text to keep</p><p>&nbsp;</p>'),
                         '<p>Some text to keep</p>')
        self.assertEqual(removeBlanks('<p>Text line 1</p><p>Text line 2</p>'),
                         '<p>Text line 1</p><p>Text line 2</p>')
        self.assertEqual(removeBlanks('<p><img src="my_image"/></p>'),
                         '<p><img src="my_image"></p>')
        # complex tree filled
        self.assertEqual(removeBlanks('<ul><li>First line</li><li>second line</li></ul>'),
                         '<ul><li>First line</li><li>second line</li></ul>')
        # complex tree semi-filled
        self.assertEqual(removeBlanks('<ul><li>First line</li><li> </li></ul>'),
                         '<ul><li>First line</li><li> </li></ul>')
        # empty complex tree, is not wiped out because master tag containing children
        self.assertEqual(removeBlanks('<ul><li>&nbsp;</li><li>&nbsp;</li></ul>'),
                         '<ul><li>&#160;</li><li>&#160;</li></ul>')
        # result is not prettyfied (pretty_print=False) but if source was
        # pretty, then the result is pretty also
        self.assertEqual(removeBlanks('<ul>\n  <li>&nbsp;</li>\n  <li>&nbsp;</li>\n</ul>\n'),
                         '<ul>\n  <li>&#160;</li>\n  <li>&#160;</li>\n</ul>\n')

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
        self.assertTrue(not xhtmlContentIsEmpty('<p><img src="my_image_path.png"></p>'))

    def test_addClassToContent(self):
        """
          This will add a CSS class to every CONTENT_TAGS find in the given xhtmlContent.
        """
        self.assertEqual(addClassToContent('<p>My text</p>', css_class='sample'),
                         '<p class="sample">My text</p>')
        self.assertEqual(addClassToContent('', css_class='sample'), '')
        self.assertEqual(addClassToContent(None, css_class='sample'), None)
        self.assertEqual(addClassToContent('text', css_class='sample'), 'text')
        # if tag is not handled, it does not change anything, by default, tags 'p' and 'li' are handled
        self.assertEqual(addClassToContent('<unhandled_tag>My text with tag not handled</unhandled_tag>',
                                           css_class='sample'),
                         '<unhandled_tag>My text with tag not handled</unhandled_tag>')
        # handled tag
        self.assertEqual(addClassToContent('<p>My text</p>', css_class='sample'),
                         '<p class="sample">My text</p>')
        # already existing class
        self.assertEqual(addClassToContent('<p class="another">My text</p>', css_class='sample'),
                         '<p class="sample another">My text</p>')
        self.assertEqual(addClassToContent(
            '<p>My text</p>'
            '<p class="class1 class2">My text</p>'
            '<p>My text</p>'
            '<p class="class3">My text</p>'
            '<unhandled_tag>My text</unhandled_tag>'
            '<span>My text</span>'
            '<p>My text</p>', css_class='sample'),
            '<p class="sample">My text</p>'
            '<p class="sample class1 class2">My text</p>'
            '<p class="sample">My text</p>'
            '<p class="sample class3">My text</p>'
            '<unhandled_tag>My text</unhandled_tag>'
            '<span class="sample">My text</span>'
            '<p class="sample">My text</p>')

    def test_addClassToLastChildren(self):
        """
          Test if adding a class to last x tags of a given XHTML content works.
          By default, this method receives following parameters :
          - xhtmlContent;
          - classNames={'p': 'ParaKWN',
                       'li': 'podItemKeepWithNext'};
          - tags=('p', 'li', );
          - numberOfChars=180.
        """
        self.assertEqual(addClassToLastChildren(''), '')
        self.assertEqual(addClassToLastChildren(None), None)
        self.assertEqual(addClassToLastChildren('text'), 'text')
        # if tag is not handled, it does not change anything, by default, tags 'p' and 'li' are handled
        self.assertEqual(addClassToLastChildren('<unhandled_tag>My text with tag not handled</unhandled_tag>'),
                         '<unhandled_tag>My text with tag not handled</unhandled_tag>')
        # now test with a single small handled tag, text size is lower than numberOfChars
        self.assertEqual(addClassToLastChildren('<p>My small text</p>'),
                         '<p class="ParaKWN">My small text</p>')
        # existing class attribute is kept
        self.assertEqual(addClassToLastChildren('<p class="myclass">My small text</p>'),
                         '<p class="ParaKWN myclass">My small text</p>')
        # test that if text is smaller than numberOfChars, several last tags are adapted
        self.assertEqual(addClassToLastChildren('<p>My small text</p><p>My small text</p>'),
                         '<p class="ParaKWN">My small text</p>'
                         '<p class="ParaKWN">My small text</p>')
        # large text, only relevant tags are adapted until numberOfChars is rechead
        self.assertEqual(addClassToLastChildren(
            '<p>13 chars line</p><p>33 characters text line text line</p><p>33 characters text line text line</p>',
            numberOfChars=60),
            '<p>13 chars line</p><p class="ParaKWN">33 characters text line text line</p>'
            '<p class="ParaKWN">33 characters text line text line</p>')
        # tags with children
        self.assertEqual(addClassToLastChildren(
            '<p>First untouched paragraph</p>'
            '<p><strong>Strong text Strong text Strong text Strong text</strong> '
            'Paragraph text Paragraph text Paragraph text</p>',
            numberOfChars=60),
            '<p>First untouched paragraph</p>'
            '<p class="ParaKWN"><strong>Strong text Strong text Strong text Strong text</strong> '
            'Paragraph text Paragraph text Paragraph text</p>')
        # test mixing different handled tags like 'ul', 'li' and 'p'
        self.assertEqual(addClassToLastChildren(
            '<p>13 chars line</p><ul><li>Line 1</li><li>Line 2</li><li>33 characters text line text line</li></ul>'
            '<p>33 characters text line text line</p>',
            numberOfChars=60),
            '<p>13 chars line</p><ul class="podBulletItemKeepWithNext">'
            '<li>Line 1</li><li>Line 2</li><li class="podItemKeepWithNext">33 '
            'characters text line text line</li></ul><p class="ParaKWN">33 '
            'characters text line text line</p>')
        # style is also applied on <ol>
        self.assertEqual(addClassToLastChildren(
            '<ol><li>Line 1</li><li>Line 2</li></ol>'),
            '<ol><li class="podItemKeepWithNext">Line 1</li><li class="podItemKeepWithNext">Line 2</li></ol>')
        # as soon as an unhandled tag is discover, adaptation stops
        self.assertEqual(addClassToLastChildren(
            '<p>13 chars line</p><img src="image.png"><p>13 chars line</p>'),
            '<p>13 chars line</p><img src="image.png"><p class="ParaKWN">13 chars line</p>')
        # test with sub tags
        self.assertEqual(addClassToLastChildren(
            '<p>Text</p><p><u><strong>dsdklm</strong></u></p>'),
            '<p class="ParaKWN">Text</p><p class="ParaKWN"><u><strong>dsdklm</strong></u></p>')
        # test every available tags
        self.assertEqual(addClassToLastChildren(
            '<p>Text</p>'
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
            numberOfChars=85),
            '<p class="ParaKWN">Text</p>'
            '<p class="ParaKWN"><strong>Strong</strong></p>'
            '<p class="ParaKWN"><span>Span</span></p>'
            '<p class="ParaKWN"><strike>Strike</strike></p>'
            '<p class="ParaKWN"><i>I</i></p>'
            '<p class="ParaKWN"><em>Em</em></p>'
            '<p class="ParaKWN"><u>U</u></p>'
            '<p class="ParaKWN"><small>Small</small></p>'
            '<p class="ParaKWN"><mark>Mark</mark></p>'
            '<p class="ParaKWN"><del>Del</del></p>'
            '<p class="ParaKWN"><ins>Ins</ins></p>'
            '<p class="ParaKWN"><sub>Sub</sub></p>'
            '<p class="ParaKWN"><sup>Sup</sup></p>')
        # does not break with unknown sub tags
        self.assertEqual(addClassToLastChildren(
            '<p><unknown><tagtag>Text</tagtag></unknown></p>'),
            '<p class="ParaKWN"><unknown><tagtag>Text</tagtag></unknown></p>')
        # special characters are transformed to HTML entities
        text = "<p>Some spécial charaçters &eacute;</p><p>&nbsp;</p>"
        self.assertEqual(
            addClassToLastChildren(text),
            '<p class="ParaKWN">Some sp&#233;cial chara&#231;ters &#233;</p>'
            '<p class="ParaKWN">&#160;</p>')
        # result is not prettyfied (pretty_print=False) but if source was
        # pretty, then the result is pretty also
        self.assertEqual(addClassToLastChildren(
            '<p>text</p>\n<img src="image.png"/>\n<p>text</p>\n'),
            '<p>text</p>\n<img src="image.png">\n<p class="ParaKWN">text</p>\n')

    def test_markEmptyTags(self):
        """
          Test if empty tags are correctly marked with a CSS class.
          markEmptyTags can receive different parameters :
          - markingClass : the class that will mark the empty tags;
          - tagTitle : if given, a 'title' attribute is added to the marked tags;
          - onlyAtTheEnd : if True, only empty tags at the end of the XHTML content are marked;
          - tags : a list of handled tags.
        """
        self.assertEqual(markEmptyTags(''), '')
        self.assertEqual(markEmptyTags(None), None)
        self.assertEqual(markEmptyTags("<p></p>"), '<p class="highlightBlankRow"></p>')
        self.assertEqual(markEmptyTags("<p> </p>"), '<p class="highlightBlankRow"> </p>')
        if six.PY3:
            self.assertEqual(markEmptyTags("<p>&nbsp;</p>"), '<p class="highlightBlankRow">\xa0</p>')
            self.assertEqual(markEmptyTags("<span>&nbsp;</span>"), '<span>\xa0</span>')
            # result is not prettyfied (pretty_print=False) but if source was
            # pretty, then the result is pretty also
            self.assertEqual(markEmptyTags('<p>String with special chars: é</p>\n'),
                             '<p>String with special chars: é</p>\n')
        else:
            self.assertEqual(markEmptyTags("<p>&nbsp;</p>"), '<p class="highlightBlankRow">\xc2\xa0</p>')
            self.assertEqual(markEmptyTags("<span>&nbsp;</span>"), '<span>\xc2\xa0</span>')
            # result is not prettyfied (pretty_print=False) but if source was
            # pretty, then the result is pretty also
            self.assertEqual(markEmptyTags(u'<p>Unicode string with special chars: \xe9</p>\n'),
                             '<p>Unicode string with special chars: \xc3\xa9</p>\n')

        self.assertEqual(markEmptyTags("<p>Text</p>"), '<p>Text</p>')
        self.assertEqual(markEmptyTags("<p>Text</p><p></p>"), '<p>Text</p><p class="highlightBlankRow"></p>')
        # change markingClass
        self.assertEqual(markEmptyTags("<p> </p>", markingClass='customClass'), '<p class="customClass"> </p>')
        # "span" not handled by default
        self.assertEqual(markEmptyTags("<span></span>"), '<span></span>')
        # but "span" could be handled if necessary
        self.assertEqual(markEmptyTags("<span></span>", tags=('span', )), '<span class="highlightBlankRow"></span>')
        # by default every empty tags are highlighted, but we can specify to highlight only trailing
        # ones aka only tags ending the XHTML content
        self.assertEqual(markEmptyTags("<p></p><p>Text</p><p></p>"),
                         '<p class="highlightBlankRow"></p><p>Text</p><p class="highlightBlankRow"></p>')
        self.assertEqual(markEmptyTags("<p></p><p>Text</p><p></p>", onlyAtTheEnd=True),
                         '<p></p><p>Text</p><p class="highlightBlankRow"></p>')
        # we can also specify to add a title attribute to the highlighted tags
        self.assertEqual(markEmptyTags("<p>Text</p><p></p>", tagTitle='My tag title'),
                         '<p>Text</p><p class="highlightBlankRow" title="My tag title"></p>')
        # if an empty tag already have a class, the marking class is appended to it
        self.assertEqual(markEmptyTags("<p class='existingClass'></p>"),
                         '<p class="highlightBlankRow existingClass"></p>')

        # we may mark Unicode as well as UTF-8 xhtmlContent
        self.assertEqual(markEmptyTags('<p>UTF-8 string with special chars: \xc3\xa9</p>'),
                         '<p>UTF-8 string with special chars: \xc3\xa9</p>')

    def test_removeCssClasses(self):
        """
          Test if given CSS classes are removed from entire xhtmlContent.
        """
        self.assertEqual(removeCssClasses(''), '')
        self.assertEqual(removeCssClasses('', css_classes=['my_class']), '')
        self.assertEqual(removeCssClasses(None), None)
        self.assertEqual(removeCssClasses(None, css_classes=['my_class']), None)
        self.assertEqual(removeCssClasses('<p></p>', css_classes=['my_class']), '<p></p>')
        self.assertEqual(removeCssClasses('<p>Text</p>', css_classes=['my_class']), '<p>Text</p>')
        self.assertEqual(removeCssClasses('<p class="another_class">Text</p>', css_classes=['my_class']),
                         '<p class="another_class">Text</p>')
        self.assertEqual(removeCssClasses('<p class="my_class">Text</p>', css_classes=['my_class']),
                         '<p>Text</p>')
        self.assertEqual(removeCssClasses('<p><span class="my_class">Text</span></p>', css_classes=['my_class']),
                         '<p><span>Text</span></p>')
        self.assertEqual(removeCssClasses(
            '<p>'
            '<span class="my_class">Text</span>'
            '<span class="another_class">Text</span>'
            '<span class="my_class">Text</span>'
            '</p>',
            css_classes=['my_class']),
            '<p>'
            '<span>Text</span>'
            '<span class="another_class">Text</span>'
            '<span>Text</span>'
            '</p>')
        self.assertEqual(removeCssClasses(
            '<ul>'
            '<li class="another_class">Text</li>'
            '<li class="my_class">Text</li>'
            '</ul>',
            css_classes=['my_class']),
            '<ul>'
            '<li class="another_class">Text</li>'
            '<li>Text</li>'
            '</ul>')
        self.assertEqual(removeCssClasses(
            '<ul>'
            '<li class="another_class"><span class="my_class">Text</span></li>'
            '<li class="my_class">Text</li>'
            '</ul>',
            css_classes=['my_class']),
            '<ul>'
            '<li class="another_class"><span>Text</span></li>'
            '<li>Text</li>'
            '</ul>')

    def test_imagesToPath(self):
        """
          Test that images src contained in a XHTML content are correctly changed to
          the blob file system absolute path.
        """
        # create a document and an image
        docId = self.portal.invokeFactory('Document', id='doc', title='Document')
        doc = getattr(self.portal, docId)
        img_without_blob_id = self.portal.invokeFactory('Image', id='img_without_blob', title='Image')
        img_without_blob = getattr(self.portal, img_without_blob_id)
        # no blob
        self.assertEqual(img_without_blob.get_size(), 0)
        data = get_file_data('dot.gif')
        img = create_image_content(self.portal, 'Image', 'img', data, filename='dot.gif')
        transaction.savepoint()
        # has a blob
        self.assertEqual(img.get_size(), 873)
        if HAS_PLONE_5_AND_MORE:
            blob = img.image._blob
        else:
            blob = img.getBlobWrapper().blob
        blob._p_activate()
        img_blob_path = blob._p_blob_committed
        # folder with doc2 to test relative path
        subfolderId = self.portal.invokeFactory('Folder', id='subfolder', title='Folder')
        subfolder = getattr(self.portal, subfolderId)
        doc2Id = subfolder.invokeFactory('Document', id='doc2', title='Document')
        doc2 = getattr(subfolder, doc2Id)

        # we do not setText because the mutator is overrided to use mxTidy
        # to prettify the HTML
        # test with internal image, absolute path
        text = '<p>Image absolute path <img src="{0}/img"> end of text.</p>'.format(self.portal_url)
        expected = text.replace("{0}/img".format(self.portal_url), img_blob_path)
        self.assertEqual(imagesToPath(doc, text).strip(), expected)
        # if we use an image having no blob, nothing is changed
        text = '<p>Image absolute path <img src="{0}/img_without_blob"> end of text.</p>'.format(self.portal_url)
        self.assertEqual(imagesToPath(doc, text).strip(), text)

        # test with internal image, relative path
        text = '<p>Image relative path <img src="../img" alt="Image" title="Image"> end of text.</p>'
        expected = text.replace("../img", img_blob_path)
        self.assertEqual(imagesToPath(doc2, text).strip(), expected)
        # if we use an image having no blob, nothing is changed
        text = '<p>Image relative path <img src="../img_without_blob" alt="Image" title="Image"> end of text.</p>'
        self.assertEqual(imagesToPath(doc2, text).strip(), text)

        # test with src to an ImageScale instead the full image
        text = '<p>Link to ImageScale absolute path <img src="{0}/img/image_preview"> '\
               'and relative path <img src="../img/image_preview">.</p>'.format(self.portal_url)
        expected = text.replace("{0}/img/image_preview".format(self.portal_url), img_blob_path)
        expected = expected.replace("../img/image_preview", img_blob_path)
        if PLONE_MAJOR_VERSION < 5:
            self.assertEqual(imagesToPath(doc2, text).strip(), expected)

        # test with src to image that is not an image, src will be to doc
        text = '<p>Src image to doc absolute path <img src="{0}/doc"> '\
               'and relative path <img src="../doc">.</p>'.format(self.portal_url)
        # left as is
        self.assertEqual(imagesToPath(doc2, text).strip(), text)

        # external image, absolute_path
        # nothing changed
        text = '<p>Image absolute path <img src="http://www.othersite.com/image.png"> end of text.</p>'
        self.assertEqual(imagesToPath(doc, text).strip(), text)

        # image that does not exist anymore, absolute and relative path
        text = '<p>Removed image absolute path <img src="{0}/removed_img"> '\
               'and relative path <img src="../removed_img">.</p>'.format(self.portal_url)
        # left as is
        self.assertEqual(imagesToPath(doc, text).strip(), text)

        # more complex case with html sublevels, relative and absolute path images
        text = """<p>Image absolute path <img src="{0}/img"> end of text.</p>
<div>
  <p>Image absolute path2 same img <img src="{0}/img"> end of text.</p>
</div>
<p>Image absolute path <img src="http://www.othersite.com/image.png"> end of text.</p>
<div>
  <p>
    <strong>Image relative path <img src="../img" alt="Image" title="Image"> end of text.</strong>
  </p>
</div>
<p>Removed image absolute path <img src="{0}/removed_img" alt="Image" title="Image"> end of text.</p>
<p>Removed image relative path <img src="../removed_img" alt="Image" title="Image"> end of text.</p>""".\
            format(self.portal_url)
        expected = text.replace("{0}/img".format(self.portal_url), img_blob_path)
        expected = expected.replace("../img", img_blob_path)
        self.assertEqual(imagesToPath(doc2, text).replace('\n', ''), expected.replace('\n', ''))

        # does not break if xhtmlContent is empty
        self.assertEqual(imagesToPath(doc, ''), '')

        # if text does not contain images, it is returned as is
        text = '<p>Text without images.</p>'
        self.assertEqual(imagesToPath(doc, text), text)

        # image outside any other tag
        text = '<img src="{0}/img/image_preview"><img src="../img/image_preview">'.format(self.portal_url)
        expected = text.replace("{0}/img/image_preview".format(self.portal_url), img_blob_path)
        expected = expected.replace("../img/image_preview", img_blob_path)
        if PLONE_MAJOR_VERSION < 5:
            self.assertEqual(imagesToPath(doc2, text).replace('\n', ''), expected.replace('\n', ''))

        # image without src, nothing done
        text = '<img title="My image without src">'
        self.assertEqual(imagesToPath(doc, text), text)

        # using resolveuid and absolute path and relative path
        text = '<img src="resolveuid/{0}/image_preview" alt="Image" title="Image">' \
               '<img src="resolveuid/{0}" alt="Image" title="Image">' \
               '<img src="{1}/img/image_preview">' \
               '<img src="../img/image_preview">'.format(img.UID(), self.portal_url)
        expected = text.replace("resolveuid/{0}/image_preview".format(img.UID()), img_blob_path)
        expected = expected.replace("resolveuid/{0}".format(img.UID()), img_blob_path)
        expected = expected.replace("{0}/img/image_preview".format(self.portal_url), img_blob_path)
        expected = expected.replace("../img/image_preview", img_blob_path)
        if PLONE_MAJOR_VERSION < 5:
            self.assertEqual(imagesToPath(doc2, text).replace('\n', ''), expected.replace('\n', ''))

        # does not break with wrong resolveuid
        if six.PY2:
            text = '<img src="resolveuid/unknown_uid" alt="Image" title="Image">'
            self.assertEqual(imagesToPath(doc2, text), text)
        else:
            text = '<img alt="Image" src="resolveuid/unknown_uid" title="Image">'
            self.assertEqual(imagesToPath(doc2, text), text)

    def test_imagesToData(self):
        """
          Test that images src contained in a XHTML content are correctly changed to
          the a data base64 value.
          Method is based on same as imagesToPath so we do not redo
          tests that are already done in test_imagesToPath.
        """
        # create a document and an image
        docId = self.portal.invokeFactory('Document', id='doc', title='Document')
        doc = getattr(self.portal, docId)
        data = get_file_data('dot.gif')
        img = create_image_content(self.portal, 'Image', 'img', data, filename='dot.gif')
        # has a blob
        self.assertEqual(img.get_size(), 873)
        text = '<p>Image <img src="{0}/img"> end of text.</p>'.format(self.portal_url)
        transaction.savepoint()
        self.assertEqual(
            imagesToData(doc, text),
            '<p>Image <img src="{0}"> end of text.</p>'.format(base64_gif_img_data))

    @require_module('Products.Archetypes')
    def test_storeExternalImagesLocally(self):
        """
          Test that images src contained in a XHTML that reference external images is
          updated correctly and external image is stored locally.
        """
        # create a document and an image
        docId = self.portal.invokeFactory('Document', id='doc', title='Document')
        doc = getattr(self.portal, docId)
        data = get_file_data('dot.gif')
        img = create_image_content(self.portal, 'Image', 'img', data, filename='dot.gif')

        # does not break if xhtmlContent is empty
        self.assertEqual(storeImagesLocally(doc, ''), '')
        self.assertEqual(storeImagesLocally(doc, '<p>&nbsp;</p>'), '<p>&nbsp;</p>')
        # not changed if only contains local images, using relative or absolute path
        text = '<p>Image absolute path <img src="/img"/> and relative path <img src="../img"/>.</p>'
        self.assertEqual(storeImagesLocally(doc, text), text)

        # link to unexisting external image, site exists but not image (error 404) nothing changed
        text = '<p>Unexisting external image <img src="http://www.imio.be/unexistingimage.png"/></p>.'
        self.assertEqual(storeImagesLocally(doc, text, replace_not_found_image=False), text)

        # link to unexisting site, nothing changed
        text = '<p>Unexisting external site <img src="http://www.unexistingsite.be/unexistingimage.png"/>.</p>'
        self.assertEqual(storeImagesLocally(doc, text, replace_not_found_image=False), text)

        # when using replace_not_found_image=True image is replaced by a "Not found" image
        text = '<p>Unexisting external image <img src="http://nohost/plone/imagenotfound.jpg"></p>.'
        self.assertEqual(storeImagesLocally(doc, text), text)
        # calling it a second time will store it again because doc is not a container
        text = '<p>Unexisting external image <img src="http://nohost/plone/imagenotfound-1.jpg"></p>.'
        self.assertEqual(storeImagesLocally(doc, text), text)

        # working example
        text = '<p>Working external image <img src="%s"/>.</p>' % picsum_image1_url
        # we have Content-Dispsition header
        downloaded_img_path, downloaded_img_infos = six.moves.urllib.request.urlretrieve(picsum_image1_url)
        self.assertTrue(downloaded_img_infos.getheader('Content-Disposition'))
        # image object does not exist for now
        self.assertFalse('10-200x300.jpg' in self.portal.objectIds())
        self.assertEqual(
            storeImagesLocally(doc, text),
            '<p>Working external image <img src="{0}/10-200x300.jpg">.</p>'.format(self.portal_url))
        img = self.portal.get('10-200x300.jpg')
        self.assertTrue(IImageContent.providedBy(img))

        # working example with a Folder, this test case where we have a container
        # using RichText field, in this case the Image is stored in the Folder, not next to it
        text = '<p>Working external image <img src="%s">.</p>' % picsum_image2_url
        expected = '<p>Working external image <img src="{0}/folder/1082-200x200.jpg">.</p>'.\
            format(self.portal_url)
        self.assertFalse('1082-200x200.jpg' in self.portal.folder.objectIds())
        self.assertEqual(storeImagesLocally(self.portal.folder, text), expected)
        mascotte = self.portal.folder.get('1082-200x200.jpg')
        self.assertTrue(IImageContent.providedBy(mascotte))

        # link to external image without Content-Disposition
        # it is downloaded nevertheless but used filename will be 'image-1'
        text = '<p>External site <img src="http://www.imio.be/logo.png">.</p>'
        expected = '<p>External site <img src="{0}/folder/image-1.png">.</p>'.format(self.portal_url)
        downloaded_img_path, downloaded_img_infos = six.moves.urllib.request.urlretrieve('http://www.imio.be/logo.png')
        self.assertIsNone(downloaded_img_infos.getheader('Content-Disposition'))
        self.assertEqual(storeImagesLocally(self.portal.folder, text), expected)
        logo = self.portal.folder.get('image-1.png')
        self.assertTrue(IImageContent.providedBy(logo))

        # if context is a container, an "Not found" image is only added one time
        testFolderId = self.portal.invokeFactory('Folder', id='testfolder', title='Test folder')
        testfolder = getattr(self.portal, testFolderId)
        text = '<p>Unexisting external site <img src="http://www.unexistingsite.be/unexistingimage.png"/>.</p>'
        expected = '<p>Unexisting external site <img src="http://nohost/plone/testfolder/imagenotfound.jpg">.</p>'
        self.assertEqual(testfolder.objectIds(), [])
        self.assertEqual(storeImagesLocally(testfolder, text), expected)
        self.assertEqual(testfolder.objectIds(), ['imagenotfound.jpg'])
        # calling it a second time with a not found image will retrieve it again
        expected = '<p>Unexisting external site <img src="http://nohost/plone/testfolder/imagenotfound-1.jpg">.</p>'
        self.assertEqual(storeImagesLocally(testfolder, text), expected)
        self.assertEqual(testfolder.objectIds(), ['imagenotfound.jpg', 'imagenotfound-1.jpg'])
        # but if image found, nothing is done
        text = '<p>Unexisting external site <img src="http://nohost/plone/testfolder/imagenotfound.jpg">.</p>'
        self.assertEqual(storeImagesLocally(testfolder, text), text)
        self.assertEqual(testfolder.objectIds(), ['imagenotfound.jpg', 'imagenotfound-1.jpg'])

    def test_storeExternalImagesLocallyWithResolveUID(self):
        """ """
        # working example
        text = '<p>Working external image <img src="%s">.</p>' % picsum_image1_url
        result = storeImagesLocally(self.portal, text, force_resolve_uid=True)

        # image was downloaded and link to it was turned to a resolveuid
        img = self.portal.get('10-200x300.jpg')
        self.assertEqual(
            result,
            '<p>Working external image <img src="resolveuid/{0}">.</p>'.format(img.UID()))

    @require_module('Products.Archetypes')
    def test_storeInternalImagesLocally(self):
        """
          Test that images src contained in a XHTML that reference internal images stored
          in another context are stored in current context.
        """
        data = get_file_data('dot.gif')
        create_image_content(self.portal, 'Image', 'dot.gif', data, filename='dot.gif')
        text = '<p>Internal image <img src="{0}/dot.gif">.</p>'.format(self.portal_url)
        expected = '<p>Internal image <img src="{0}/folder/dot.gif">.</p>'.format(self.portal_url)
        # image was created in folder
        self.assertEqual(
            storeImagesLocally(self.portal.folder, text), expected)
        image = self.portal.folder.get('dot.gif')
        self.assertTrue(IImageContent.providedBy(image))

        # nothing changed if image already stored to context
        self.assertEqual(
            storeImagesLocally(self.portal.folder, expected), expected)

        # now check when internal image does not exist
        text = '<p>Internal image <img src="{0}/unknown.gif">.</p>'.format(self.portal_url)
        # with replace_not_found_image=False in case an internal image is not found, nothing is done
        self.assertEqual(
            storeImagesLocally(self.portal.folder, text, replace_not_found_image=False),
            text)
        text = '<p>Internal image <img src="http://nohost/plone/folder/imagenotfound.jpg">.</p>'
        self.assertEqual(
            storeImagesLocally(self.portal.folder, text, replace_not_found_image=True),
            text)

    def test_storeInternalImagesLocallyWithResolveUID(self):
        """ """
        file_path = os.path.join(os.path.dirname(__file__), 'dot.gif')
        fd = open(file_path, 'rb')
        data = fd.read()
        create_image_content(self.portal, 'Image', 'dot.gif', data=data)
        img2 = create_image_content(self.portal, 'Image 2', 'dot2.gif', data=data)
        img3 = create_image_content(self.portal, 'Image 3', 'dot3.gif', data=data)
        img4 = create_image_content(self.portal, 'Image 4', 'dot4.gif', data=data)
        img5 = create_image_content(self.portal, 'Image 5', 'dot5.gif', data=data)
        fd.close()
        text = '<p>Int img full url <img src="{0}/dot.gif"/>.</p>' \
            '<p>Int img resolveuid <img src="resolveuid/{1}"/>.</p>' \
            '<p>Int img resolveuid and image_preview <img src="resolveuid/{2}/image_preview"/>.</p>' \
            '<p>Int img resolveuid portal_url <img src="{0}/resolveuid/{3}"/>.</p>' \
            '<p>Int img resolveuid portal_url image_preview <img src="{0}/resolveuid/{4}/image_preview"/>.</p>'.format(
                self.portal_url, img2.UID(), img3.UID(), img4.UID(), img5.UID())

        # every images uri are turned to resolveuid
        result = storeImagesLocally(self.portal.folder, text, force_resolve_uid=True)
        # images were created in folder
        self.assertEqual(
            self.portal.folder.objectIds(),
            ['dot.gif', 'dot2.gif', 'dot3.gif', 'dot4.gif', 'dot5.gif'])
        new_img = self.portal.folder.get('dot.gif')
        new_img2 = self.portal.folder.get('dot2.gif')
        new_img3 = self.portal.folder.get('dot3.gif')
        new_img4 = self.portal.folder.get('dot4.gif')
        new_img5 = self.portal.folder.get('dot5.gif')
        expected = '<p>Int img full url <img src="resolveuid/{0}">.</p>' \
            '<p>Int img resolveuid <img src="resolveuid/{1}">.</p>' \
            '<p>Int img resolveuid and image_preview <img src="resolveuid/{2}/image_preview">.</p>' \
            '<p>Int img resolveuid portal_url <img src="resolveuid/{3}">.</p>' \
            '<p>Int img resolveuid portal_url image_preview <img src="resolveuid/{4}/image_preview">.</p>'.format(
                new_img.UID(), new_img2.UID(), new_img3.UID(), new_img4.UID(), new_img5.UID())
        self.assertEqual(result, expected)

    def test_storeImagesLocallyWithWrongSrc(self):
        """Do not fail when no src in the <img> tag or src is to something else than an image."""
        # no src
        text = '<p>Text <img style="width: 50px; height: 50px;"/>.</p>'
        # nothing was changed
        self.assertEqual(storeImagesLocally(self.portal.folder, text), text)

        # src to a non Image, Folder
        text = '<p>Text <img src="{0}"style="width: 50px; height: 50px;"/>.</p>'.format(
            self.portal.absolute_url())
        # nothing was changed
        self.assertEqual(
            storeImagesLocally(self.portal.folder, text, replace_not_found_image=False),
            text)

        # src to a non Image, Portal
        text = '<p>Text <img src="{0}"style="width: 50px; height: 50px;"/>.</p>'.format(
            self.portal.folder.absolute_url())
        # nothing was changed
        self.assertEqual(
            storeImagesLocally(self.portal.folder2, text, replace_not_found_image=False),
            text)

    def test_storeImagesLocallyWithImgPathStoredInFolderStartingWithContextURL(self):
        """Make sure an image stored in a folder that have same id as begining
           of another folder the image is stored in downloads the image."""

        self.assertTrue(self.portal.folder2.absolute_url().startswith(
            self.portal.folder.absolute_url()))

        text = '<p>Working external image <img src="%s">.</p>' % picsum_image1_url
        storeImagesLocally(self.portal.folder2, text)
        text = '<p>Working external image <img src="{0}">.</p>'.format(
            self.portal.folder2.objectValues()[0].absolute_url()
        )
        self.assertFalse(self.portal.folder.objectIds())
        storeImagesLocally(self.portal.folder, text)
        self.assertTrue(self.portal.folder.objectIds())

    def test_storeExternalImagesLocallyImageURLWithNonASCIIChars(self):
        """URL to image may contain non ASCII chars."""
        text = '<p>External image with special chars <img src="http://www.imio.be/émage.png">.</p>'
        result = storeImagesLocally(self.portal, text, force_resolve_uid=True, replace_not_found_image=False)
        # in this case, image is ignored
        self.assertEqual(result, text)

    def test_storeExternalImagesLocallyDataBase64Image(self):
        """Test when src is a data:image base64 encoded image."""
        if six.PY3:
            self.skipTest('Skipped for py3: storeImagesLocally broken with base64 image, downloaded_img_infos is '
                          '<email.message.Message object')
        text = '<p>Image using data:image base64 encoded binary.</p>' \
            '<p><img src="{0}" /></p><p><img src="{0}" /></p>'.format(base64_img_data)
        expected = '<p>Image using data:image base64 encoded binary.</p>' \
            '<p><img src="http://nohost/plone/image-1.png"></p>' \
            '<p><img src="http://nohost/plone/image-2.png"></p>'
        # for now, no images
        self.assertEqual(len([obj for obj in self.portal.objectValues()
                         if obj.portal_type == "Image"]), 0)
        result = storeImagesLocally(self.portal, text)
        self.assertEqual(result, expected)
        self.assertEqual(len([obj for obj in self.portal.objectValues()
                         if obj.portal_type == "Image"]), 2)

    def test_object_link(self):
        obj = self.portal.folder
        obj.setTitle(u'Folder title')
        self.assertEqual(object_link(obj), u'<a href="http://nohost/plone/folder/view">Folder title</a>')
        self.assertEqual(object_link(obj, view='edit'),
                         u'<a href="http://nohost/plone/folder/edit">Folder title</a>')
        self.assertEqual(object_link(obj, attribute='portal_type'),
                         u'<a href="http://nohost/plone/folder/view">Folder</a>')
        self.assertEqual(object_link(obj, view='edit', attribute='Description'),
                         u'<a href="http://nohost/plone/folder/edit"></a>')
        self.assertEqual(object_link(obj, view='edit', attribute='Description', target='_blank'),
                         u'<a href="http://nohost/plone/folder/edit" target="_blank"></a>')
        obj.setTitle(u'Folder title <script />')
        self.assertEqual(object_link(obj),
                         u'<a href="http://nohost/plone/folder/view">Folder title &lt;script /&gt;</a>')
        self.assertEqual(object_link(obj, escaped=False),
                         u'<a href="http://nohost/plone/folder/view">Folder title <script /></a>')

    def test_separate_images(self):
        # no image, content is returned as is
        text = '<p>My text.</p><p>My text.</p><p>My text.</p>'
        result = separate_images(text)
        self.assertEqual(text, result)
        # one image, nothing changed
        text = '<p><img src="http://plone/nohost/image1.png"></p>'
        result = separate_images(text)
        self.assertEqual(text, result)
        # one image with text, nothing changed
        text = '<p><img src="http://plone/nohost/image1.png">.</p>'
        result = separate_images(text)
        self.assertEqual(text, result)
        # one image with text, nothing changed
        text = '<p>Example : <img src="http://plone/nohost/image1.png"></p>'
        result = separate_images(text)
        self.assertEqual(text, result)
        # 2 images with text, nothing changed
        text = '<p>Example : <img src="http://plone/nohost/image1.png">' \
            '<img src="http://plone/nohost/image2.png"></p>'
        result = separate_images(text)
        self.assertEqual(text, result)

        # <p> containg other tags than <img>, nothing changed
        text = '<p><img src="http://plone/nohost/image1.png">' \
            '<img src="http://plone/nohost/image2.png"><span>Text</span></p>'
        result = separate_images(text)
        self.assertEqual(text, result)

        # now working examples
        # 2 images
        text = '<p><img src="http://plone/nohost/image1.png">' \
            '<img src="http://plone/nohost/image2.png"></p>'
        result = separate_images(text)
        self.assertEqual(result, '<p><img src="http://plone/nohost/image1.png"></p>'
                         '<p><img src="http://plone/nohost/image2.png"></p>')
        # 3 images
        text = '<p><img src="http://plone/nohost/image1.png">' \
            '<img src="http://plone/nohost/image2.png">' \
            '<img src="http://plone/nohost/image3.png"></p>'
        result = separate_images(text)
        self.assertEqual(result, '<p><img src="http://plone/nohost/image1.png"></p>'
                         '<p><img src="http://plone/nohost/image2.png"></p>'
                         '<p><img src="http://plone/nohost/image3.png"></p>')
        # complex case
        text = '<p>My text and so on...</p>' \
            '<p><img src="http://plone/nohost/image1.png"></p>' \
            '<p><img src="http://plone/nohost/image2.png">' \
            '<img src="http://plone/nohost/image3.png"></p>' \
            '<p>Some other text...</p>' \
            '<p><img src="http://plone/nohost/image4.png"></p>'
        result = separate_images(text)
        self.assertEqual(result, '<p>My text and so on...</p>'
                         '<p><img src="http://plone/nohost/image1.png"></p>'
                         '<p><img src="http://plone/nohost/image2.png"></p>'
                         '<p><img src="http://plone/nohost/image3.png"></p>'
                         '<p>Some other text...</p>'
                         '<p><img src="http://plone/nohost/image4.png"></p>')
        # very complex case
        text = '<p>My text and so on...</p>' \
            '<p><img src="http://plone/nohost/image1.png"></p>' \
            '<div><img src="http://plone/nohost/image2.png">' \
            '<img src="http://plone/nohost/image3.png"></div>' \
            '<p>Some other text...</p>' \
            '<p><img src="http://plone/nohost/image4.png">' \
            '<img src="http://plone/nohost/image5.png"></p>' \
            '<p><img src="http://plone/nohost/image6.png"></p>' \
            '<table><tr><td><p><img src="http://plone/nohost/image7.png">' \
            '<img src="http://plone/nohost/image8.png"></p></td></tr></table>'
        result = separate_images(text)
        self.assertEqual(result, '<p>My text and so on...</p>'
                         '<p><img src="http://plone/nohost/image1.png"></p>'
                         '<div><img src="http://plone/nohost/image2.png"></div>'
                         '<div><img src="http://plone/nohost/image3.png"></div>'
                         '<p>Some other text...</p>'
                         '<p><img src="http://plone/nohost/image4.png"></p>'
                         '<p><img src="http://plone/nohost/image5.png"></p>'
                         '<p><img src="http://plone/nohost/image6.png"></p>'
                         '<table><tr><td><p><img src="http://plone/nohost/image7.png">'
                         '<img src="http://plone/nohost/image8.png"></p></td></tr></table>')
        # <br> are ignored
        text = '<p><img src="http://plone/nohost/image1.png"><br><br />' \
            '<img src="http://plone/nohost/image2.png"></p>'
        result = separate_images(text)
        self.assertEqual(result, '<p><img src="http://plone/nohost/image1.png"><br><br></p>'
                         '<p><img src="http://plone/nohost/image2.png"></p>')
        # blanks are ignored
        text = '<p><img src="http://plone/nohost/image1.png">&nbsp; &nbsp;' \
            '<img src="http://plone/nohost/image2.png"></p>'
        result = separate_images(text)
        if six.PY2:
            self.assertEqual(result, '<p><img src="http://plone/nohost/image1.png">\xc2\xa0 \xc2\xa0</p>'
                             '<p><img src="http://plone/nohost/image2.png"></p>')
        else:
            self.assertEqual(result, '<p><img src="http://plone/nohost/image1.png">\xa0 \xa0</p>'
                                     '<p><img src="http://plone/nohost/image2.png"></p>')
        # blanks and <br> are ignored as well
        text = '<p><img src="http://plone/nohost/image1.png">&nbsp; &nbsp;<br>' \
            '<img src="http://plone/nohost/image2.png"></p>'
        result = separate_images(text)
        if six.PY2:
            self.assertEqual(result, '<p><img src="http://plone/nohost/image1.png">\xc2\xa0 \xc2\xa0<br></p>'
                             '<p><img src="http://plone/nohost/image2.png"></p>')
        else:
            self.assertEqual(result, '<p><img src="http://plone/nohost/image1.png">\xa0 \xa0<br></p>'
                             '<p><img src="http://plone/nohost/image2.png"></p>')

    def test_replace_content(self):
        text = '<p>Text <span class="to-hide">hidden</span> some other text.</p>' \
            '<p>Text <span class="to-hide">hidden <strong>hidden</strong> hidden</span> some other text.</p>' \
            '<p><span class="to-hide">hidden</span> some other text.</p>' \
            '<p><span class="to-hide">hidden</span></p>' \
            '<p><span class="to-hide">hidden</span></p>' \
            '<table><tr><td>Text <span class="to-hide">hidden</span></td>' \
            '<td>Text not hidden</td></tr></table>'
        expected = '<p>Text <span class="to-hide"></span> some other text.</p>' \
            '<p>Text <span class="to-hide"></span> some other text.</p>' \
            '<p><span class="to-hide"></span> some other text.</p>' \
            '<p><span class="to-hide"></span></p>' \
            '<p><span class="to-hide"></span></p>' \
            '<table><tr><td>Text <span class="to-hide"></span></td>' \
            '<td>Text not hidden</td></tr></table>'
        expected_new_content = '<p>Text <span class="to-hide">replaced</span> some other text.</p>' \
            '<p>Text <span class="to-hide">replaced</span> some other text.</p>' \
            '<p><span class="to-hide">replaced</span> some other text.</p>' \
            '<p><span class="to-hide">replaced</span></p>' \
            '<p><span class="to-hide">replaced</span></p>' \
            '<table><tr><td>Text <span class="to-hide">replaced</span></td>' \
            '<td>Text not hidden</td></tr></table>'
        res = replace_content(text, css_class="to-hide")
        self.assertEqual(res, expected)
        res = replace_content(text, css_class="to-hide", new_content=u"replaced")
        self.assertEqual(res, expected_new_content)
        text_link = '<p>Text <span class="to-hide">hidden <strong>hidden</strong></span></p>'
        expected_link = '<p>Text <span class="to-hide">' \
            '<a href="https://python.org" title="Explanation">replaced</a></span></p>'
        res = replace_content(
            text_link,
            css_class="to-hide",
            new_content=u"replaced",
            new_content_link={
                "href": "https://python.org",
                "title": u"Explanation"})
        self.assertEqual(res, expected_link)
        # every sub content is removed
        text_with_sub = '<p>Text <span class="to-hide"><span class="highlight">hidden</span>' \
            '</span> some other text.</p>'
        expected_text_with_sub = '<p>Text <span class="to-hide">replaced</span> some other text.</p>'
        res = replace_content(
            text_with_sub,
            css_class="to-hide",
            new_content=u"replaced")
        self.assertEqual(res, expected_text_with_sub)

    def test_is_html(self):
        self.assertFalse(is_html(None))
        self.assertFalse(is_html(""))
        self.assertFalse(is_html("None"))
        self.assertTrue(is_html("<p>My text</p>"))
        self.assertTrue(is_html("<p>My text <span>text 2</span>.</p>"))

    def test_unescape_html(self):
        self.assertIsNone(unescape_html(None))
        self.assertEqual(unescape_html(""), "")
        self.assertEqual(unescape_html(u""), u"")
        self.assertEqual(unescape_html("<p>Activit&#233; scolaire</p>"), "<p>Activité scolaire</p>")
        self.assertEqual(unescape_html(u"<p>Activit&#233; scolaire</p>"), u"<p>Activité scolaire</p>")
