# -*- coding: utf-8 -*-
import urllib
from os import path

from Products.ATContentTypes.interfaces import IImageContent

from imio.helpers.testing import IntegrationTestCase
from imio.helpers.xhtml import addClassToContent
from imio.helpers.xhtml import addClassToLastChildren
from imio.helpers.xhtml import imagesToPath
from imio.helpers.xhtml import markEmptyTags
from imio.helpers.xhtml import removeBlanks
from imio.helpers.xhtml import removeCssClasses
from imio.helpers.xhtml import storeExternalImagesLocally
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
        self.assertEqual(removeBlanks(''), '')
        self.assertEqual(removeBlanks(None), None)
        self.assertEqual(removeBlanks('<p></p>'), '')
        self.assertEqual(removeBlanks('<p></p><br><br /><br/>'), '')
        self.assertEqual(removeBlanks('<p>&nbsp;</p>'), '')
        self.assertEqual(removeBlanks('<p>&nbsp;<p><p>&nbsp;</p><i></i>'), '')
        self.assertEqual(removeBlanks('<p>Some text to keep</p><p>&nbsp;</p><i></i>'),
                         '<p>Some text to keep</p>')
        self.assertEqual(removeBlanks('<p> </p><p>Some text to keep</p><p>&nbsp;</p>'),
                         '<p>Some text to keep</p>')
        self.assertEqual(removeBlanks('<p>Text line 1</p><p>Text line 2</p>'),
                         '<p>Text line 1</p><p>Text line 2</p>')
        self.assertEqual(removeBlanks('<p><img src="my_image"/></p>'),
                         '<p><img src="my_image"/></p>')
        # complex tree filled
        self.assertEqual(removeBlanks('<ul><li>First line</li><li>second line</li></ul>'),
                         '<ul><li>First line</li><li>second line</li></ul>')
        # complex tree semi-filled
        self.assertEqual(removeBlanks('<ul><li>First line</li><li></li></ul>'),
                         '<ul><li>First line</li><li/></ul>')
        # empty complex tree, is not wiped out because master tag containing children
        self.assertEqual(removeBlanks('<ul><li></li><li></li></ul>'),
                         '<ul><li/><li/></ul>')
        # result is not prettyfied (pretty_print=False) but if source was
        # pretty, then the result is pretty also
        self.assertEqual(removeBlanks('<ul>\n  <li/>\n  <li/>\n</ul>\n'),
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
            '<p>13 chars line</p><img src="image.png"/><p>13 chars line</p>'),
            '<p>13 chars line</p><img src="image.png"/><p class="ParaKWN">13 chars line</p>')
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
            '<p>text</p>\n<img src="image.png"/>\n<p class="ParaKWN">text</p>\n')

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
        self.assertEqual(markEmptyTags("<p></p>"), '<p class="highlightBlankRow"/>')
        self.assertEqual(markEmptyTags("<p> </p>"), '<p class="highlightBlankRow"> </p>')
        self.assertEqual(markEmptyTags("<p>Text</p>"), '<p>Text</p>')
        self.assertEqual(markEmptyTags("<p>Text</p><p></p>"), '<p>Text</p><p class="highlightBlankRow"/>')
        # change markingClass
        self.assertEqual(markEmptyTags("<p> </p>", markingClass='customClass'), '<p class="customClass"> </p>')
        # "span" not handled by default
        self.assertEqual(markEmptyTags("<span></span>"), '<span/>')
        # but "span" could be handled if necessary
        self.assertEqual(markEmptyTags("<span></span>", tags=('span', )), '<span class="highlightBlankRow"/>')
        # by default every empty tags are highlighted, but we can specify to highlight only trailing
        # ones aka only tags ending the XHTML content
        self.assertEqual(markEmptyTags("<p></p><p>Text</p><p></p>"),
                         '<p class="highlightBlankRow"/><p>Text</p><p class="highlightBlankRow"/>')
        self.assertEqual(markEmptyTags("<p></p><p>Text</p><p></p>", onlyAtTheEnd=True),
                         '<p/><p>Text</p><p class="highlightBlankRow"/>')
        # we can also specify to add a title attribute to the highlighted tags
        self.assertEqual(markEmptyTags("<p>Text</p><p></p>", tagTitle='My tag title'),
                         '<p>Text</p><p class="highlightBlankRow" title="My tag title"/>')
        # if an empty tag already have a class, the marking class is appended to it
        self.assertEqual(markEmptyTags("<p class='existingClass'></p>"),
                         '<p class="highlightBlankRow existingClass"/>')

        # we may mark Unicode as well as UTF-8 xhtmlContent
        self.assertEqual(markEmptyTags('<p>UTF-8 string with special chars: \xc3\xa9</p>'),
                         '<p>UTF-8 string with special chars: \xc3\xa9</p>')
        self.assertEqual(markEmptyTags(u'<p>Unicode string with special chars: \xe9</p>'),
                         '<p>Unicode string with special chars: \xc3\xa9</p>')
        # result is not prettyfied (pretty_print=False) but if source was
        # pretty, then the result is pretty also
        self.assertEqual(markEmptyTags(u'<p>Unicode string with special chars: \xe9</p>\n'),
                         '<p>Unicode string with special chars: \xc3\xa9</p>\n')

    def test_removeCssClasses(self):
        """
          Test if given CSS classes are removed from entire xhtmlContent.
        """
        self.assertEqual(removeCssClasses(''), '')
        self.assertEqual(removeCssClasses('', css_classes=['my_class']), '')
        self.assertEqual(removeCssClasses(None), None)
        self.assertEqual(removeCssClasses(None, css_classes=['my_class']), None)
        self.assertEqual(removeCssClasses('<p></p>', css_classes=['my_class']), '<p/>')
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
        file_path = path.join(path.dirname(__file__), 'dot.gif')
        data = open(file_path, 'r')
        img = self.portal.invokeFactory('Image', id='img', title='Image', file=data.read())
        img = getattr(self.portal, img)
        # has a blob
        self.assertEqual(img.get_size(), 873)
        img_blob_path = img.getBlobWrapper().blob._p_blob_committed
        # folder with doc2 to test relative path
        subfolderId = self.portal.invokeFactory('Folder', id='subfolder', title='Folder')
        subfolder = getattr(self.portal, subfolderId)
        doc2Id = subfolder.invokeFactory('Document', id='doc2', title='Document')
        doc2 = getattr(subfolder, doc2Id)

        # we do not setText because the mutator is overrided to use mxTidy
        # to prettify the HTML
        # test with internal image, absolute path
        text = '<p>Image absolute path <img src="http://nohost/plone/img"/> end of text.</p>'
        expected = text.replace("http://nohost/plone/img", img_blob_path)
        self.assertEqual(imagesToPath(doc, text).strip(), expected)
        # if we use an image having no blob, nothing is changed
        text = '<p>Image absolute path <img src="http://nohost/plone/img_without_blob"/> end of text.</p>'
        self.assertEqual(imagesToPath(doc, text).strip(), text)

        # test with internal image, relative path
        text = '<p>Image relative path <img src="../img" alt="Image" title="Image"/> end of text.</p>'
        expected = text.replace("../img", img_blob_path)
        self.assertEqual(imagesToPath(doc2, text).strip(), expected)
        # if we use an image having no blob, nothing is changed
        text = '<p>Image relative path <img src="../img_without_blob" alt="Image" title="Image"/> end of text.</p>'
        self.assertEqual(imagesToPath(doc2, text).strip(), text)

        # test with src to an ImageScale instead the full image
        text = '<p>Link to ImageScale absolute path <img src="http://nohost/plone/img/image_preview"/> '\
               'and relative path <img src="../img/image_preview"/>.</p>'
        expected = text.replace("http://nohost/plone/img/image_preview", img_blob_path)
        expected = expected.replace("../img/image_preview", img_blob_path)
        self.assertEqual(imagesToPath(doc2, text).strip(), expected)

        # test with src to image that is not an image, src will be to doc
        text = '<p>Src image to doc absolute path <img src="http://nohost/plone/doc"/> '\
               'and relative path <img src="../doc"/>.</p>'
        # left as is
        self.assertEqual(imagesToPath(doc2, text).strip(), text)

        # external image, absolute_path
        # nothing changed
        text = '<p>Image absolute path <img src="http://www.othersite.com/image.png"/> end of text.</p>'
        self.assertEqual(imagesToPath(doc, text).strip(), text)

        # image that does not exist anymore, absolute and relative path
        text = '<p>Removed image absolute path <img src="http://nohost/plone/removed_img"/> '\
               'and relative path <img src="../removed_img"/>.</p>'
        # left as is
        self.assertEqual(imagesToPath(doc, text).strip(), text)

        # more complex case with html sublevels, relative and absolute path images
        text = """<p>Image absolute path <img src="http://nohost/plone/img"/> end of text.</p>
<div>
  <p>Image absolute path2 same img <img src="http://nohost/plone/img"/> end of text.</p>
</div>
<p>Image absolute path <img src="http://www.othersite.com/image.png"/> end of text.</p>
<div>
  <p>
    <strong>Image relative path <img src="../img" alt="Image" title="Image"/> end of text.</strong>
  </p>
</div>
<p>Removed image absolute path <img src="http://nohost/plone/removed_img" alt="Image" title="Image"/> end of text.</p>
<p>Removed image relative path <img src="../removed_img" alt="Image" title="Image"/> end of text.</p>"""
        expected = text.replace("http://nohost/plone/img", img_blob_path)
        expected = expected.replace("../img", img_blob_path)
        self.assertEqual(imagesToPath(doc2, text).replace('\n', ''), expected.replace('\n', ''))

        # does not break if xhtmlContent is empty
        self.assertEqual(imagesToPath(doc, ''), '')

        # if text does not contain images, it is returned as is
        text = '<p>Text without images.</p>'
        self.assertEqual(imagesToPath(doc, text), text)

        # image outside any other tag
        text = '<img src="http://nohost/plone/img/image_preview"/><img src="../img/image_preview"/>'
        expected = text.replace("http://nohost/plone/img/image_preview", img_blob_path)
        expected = expected.replace("../img/image_preview", img_blob_path)
        self.assertEqual(imagesToPath(doc2, text).replace('\n', ''), expected.replace('\n', ''))

        # using resolveuid and absolute path and relative path
        text = '<img src="resolveuid/{0}/image_preview" alt="Image" title="Image"/>' \
               '<img src="resolveuid/{0}" alt="Image" title="Image"/>' \
               '<img src="http://nohost/plone/img/image_preview"/>' \
               '<img src="../img/image_preview"/>'.format(img.UID())
        expected = text.replace("resolveuid/{0}/image_preview".format(img.UID()), img_blob_path)
        expected = expected.replace("resolveuid/{0}".format(img.UID()), img_blob_path)
        expected = expected.replace("http://nohost/plone/img/image_preview", img_blob_path)
        expected = expected.replace("../img/image_preview", img_blob_path)
        self.assertEqual(imagesToPath(doc2, text).replace('\n', ''), expected.replace('\n', ''))

    def test_storeExternalImagesLocally(self):
        """
          Test that images src contained in a XHTML that reference external images is
          updated correctly and external image is stored locally.
        """
        # create a document and an image
        docId = self.portal.invokeFactory('Document', id='doc', title='Document')
        doc = getattr(self.portal, docId)
        file_path = path.join(path.dirname(__file__), 'dot.gif')
        data = open(file_path, 'r')
        img = self.portal.invokeFactory('Image', id='img', title='Image', file=data.read())
        img = getattr(self.portal, img)

        # does not break if xhtmlContent is empty
        self.assertEqual(storeExternalImagesLocally(doc, ''), '')
        self.assertEqual(storeExternalImagesLocally(doc, '<p>&nbsp;</p>'), '<p>&nbsp;</p>')
        # not changed if only contains local images, using relative or absolute path
        text = '<p>Image absolute path <img src="http://nohost/plone/img"/> '\
               'and relative path <img src="../img"/>.</p>'
        self.assertEqual(storeExternalImagesLocally(doc, text), text)

        # link to unexisting external image, site exists but not image (error 404) nothing changed
        text = '<p>Unexisting external image <img src="http://www.imio.be/unexistingimage.png"/></p>.'
        self.assertEqual(storeExternalImagesLocally(doc, text), text)

        # link to unexisting site, nothing changed
        text = '<p>Unexisting external site <img src="http://www.unexistingsite.be/unexistingimage.png"/>.</p>'
        self.assertEqual(storeExternalImagesLocally(doc, text), text)

        # working example
        text = '<p>Working external image <img src="http://www.imio.be/contact.png"/>.</p>'
        # we have Content-Dispsition header
        downloaded_img_path, downloaded_img_infos = urllib.urlretrieve('http://www.imio.be/contact.png')
        self.assertTrue(downloaded_img_infos.getheader('Content-Disposition'))
        # image object does not exist for now
        self.assertFalse('contact.png' in self.portal.objectIds())
        self.assertEqual(storeExternalImagesLocally(doc, text),
                         '<p>Working external image <img src="http://nohost/plone/contact.png"/>.</p>')
        contact = self.portal.get('contact.png')
        self.assertTrue(IImageContent.providedBy(contact))

        # working example with a Folder, this test case where we have a container
        # using RichText field, in this case the Image is stored in the Folder, not next to it
        text = '<p>Working external image <img src="http://www.imio.be/mascotte-presentation.jpg"/>.</p>'
        expected = '<p>Working external image <img src="http://nohost/plone/folder/mascotte-presentation.jpg"/>.</p>'
        self.assertFalse('mascotte-presentation.jpg' in self.portal.folder.objectIds())
        self.assertEqual(storeExternalImagesLocally(self.portal.folder, text), expected)
        mascotte = self.portal.folder.get('mascotte-presentation.jpg')
        self.assertTrue(IImageContent.providedBy(mascotte))

        # link to external image without Content-Disposition
        # it is downloaded nevertheless but used filename will be 'image-1'
        text = '<p>External site <img src="http://www.imio.be/logo.png"/>.</p>'
        expected = '<p>External site <img src="http://nohost/plone/folder/image-1.png"/>.</p>'
        downloaded_img_path, downloaded_img_infos = urllib.urlretrieve('http://www.imio.be/logo.png')
        self.assertIsNone(downloaded_img_infos.getheader('Content-Disposition'))
        self.assertEqual(storeExternalImagesLocally(self.portal.folder, text), expected)
        logo = self.portal.folder.get('image-1.png')
        self.assertTrue(IImageContent.providedBy(logo))
