Changelog
=========

0.4.24 (2017-02-14)
-------------------

- In content.validate_fields, initialize field by calling bind(obj) so
  necessary things like vocabularies are available.
  [gbastien]

0.4.23 (2017-02-14)
-------------------

- Added content module test.
  [sgeulette]
- Improved get_object, add_image, add_file, create methods
  [sgeulette]
- Added content.validate_fields that will validate fields of
  a given dexterity obj.
  [gbastien]

0.4.22 (2016-12-21)
-------------------

- Added more usecases to test appy.pod rendering : 'text-decoration: none;',
  complex and reallife table examples, ...
  [gbastien]
- Added method xhtml.removeCssClasses to be able to remove some specific Css
  classes from a given xhtmlContent.
  [gbastien]

0.4.21 (2016-12-05)
-------------------

- Added method xhtml.addClassToContent that gives the ability to add a CSS class
  to the CONTENT_TAGS (<p>, <strong>, ...) of a given xhtmlContent.
  [gbastien]
- Add @volatile_cache_without_parameters and
  @volatile_cache_with_parameters decorators
  [mpeeters]
- Store the volatile keys on a dictionary on the portal
  [mpeeters]
- Can add a file to an object.
  [sgeulette]
- Added case in 'appy_pod_sample' to check when style attribute is used to
  define italic/bold/underline/strike directly on <li> or on <li> containing
  <p> or <span>.
  [gbastien]


0.4.20 (2016-10-05)
-------------------

- Added 'path' module with method 'path_to_package' that will return the absolute
  FS path to a given package.  An extra 'filepart' can be provided to complete the
  returned path.  This is useful to get a template in a 'browser/template' folder
  for example.
  [gbastien]


0.4.19 (2016-09-26)
-------------------

- Do not pretty_print HTML returned by lxml.html.tostring or it can leads to
  weird behaviors like extra blank space in case we have nested <span> tags.
  'pretty_print' is now a parameter to relevant methods and is False by default
  [gbastien]
- Added methods to create content from a dictionary, to get object following
  criterias, to apply multiple transitions, to create a RichTextValue object
  [sgeulette]
- Added default views for Dexterity content and container that display
  fields in a table with widget label and the left and widget value on
  the right.  The view for container also includes an asynchronous
  folder_listing that lists contained elements.
  Taken from imio.project.core
  [gbastien]


0.4.18 (2016-06-17)
-------------------

- Use by default scale=2 instead of scale=4 when generating barcode.
  [gbastien]
- Added methods int2word, wordizeDate and formatDate aiming to transform
  numbers into french translation, date with only numbers into date in full
  and to format dates (with hours, with month name in full, ...).
  [DieKatze]


0.4.17 (2016-03-22)
-------------------

- Added constant CLASS_TO_LAST_CHILDREN_NUMBER_OF_CHARS_DEFAULT to define the
  default number of characters to take into account while marking last tags
  in xhtml.addClassToLastChildren.  This way it can be used in other packages.
  [gbastien]
- Fixed xhtml.imagesToPath to handle image src using 'resolveuid' correctly.
  [gbastien]


0.4.16 (2016-03-14)
-------------------

- Bugfix in xhtml.storeExternalImagesLocally if downloaded external image has
  no 'Content-Disposition' header.
  [gbastien]


0.4.15 (2016-03-14)
-------------------

- Added helper to be able to easily test appy.pod rendering by loading a full
  HTML content to any content (AT or DX) by specifying a RichText field_name.
  [gbastien]
- Added method xhtml.imagesToPath that turns the src of images used in a xhtml
  content from an 'http' or equivalent path to the absolute path on the FileSystem
  to the .blob image file.
  [gbastien]
- Added method xhtml.storeExternalImagesLocally that will ensure that externally
  referenced images are downloaded, stored locally and xhtmlContent is adapted
  accordingly.
  [gbastien]


0.4.14 (2016-02-25)
-------------------

- Added methods cache.get_cachekey_volatile and
  cache.invalidate_cachekey_volatile_for to be used with methods using
  decorator @ram.cache.  This is meant for long living cached methods that are
  invalidated manually. get_cachekey_volatile will be used in the method
  cachekey and invalidate_cachekey_volatile_for will be used to invalidate the
  cachekey.
  [gbastien]
- Add a function to generate a barcode with zint : #13100.
  [mpeeters]
- Removed initialize() call from __init__, no need to be considered
  as a Zope2 product.
  [gbastien]


0.4.13 (2016-01-22)
-------------------

- Use safe_unicode() instead of unicode(), especially in xhtml.markEmptyTags
  to avoid UnicideDecode errors.
  [gbastien]


0.4.12 (2016-01-21)
-------------------

- Added test when an uid (path) is no more in the portal_catalog,
  it does not break catalog.addOrUpdateColumns.
  [gbastien]
- In xhtml.xhtmlContentIsEmpty, do no more consider tag children in _isEmpty,
  a tag rendering nothing (text_content().strip() is empty) will be considered empty.
  [gbastien]


0.4.11 (2015-11-12)
-------------------

- Added 'cache.cleanRamCache' method that will invalidateAll ram.cache.
  [gbastien]


0.4.10 (2015-08-21)
-------------------

- Add get_environment method and test.
  [bsuttor]
- is_develop_environment method is true if global environment variable 'ENV' is equal to 'dev'.
  [bsuttor]
- Added 'cache' module with helper methods 'cleanVocabularyCacheFor' that will clean
  instance.memoize cache defined on a named vocabulary and 'cleanRamCacheFor' that
  will clean ram.cache defined on a given method.
  [gbastien]


0.4.9 (2015-04-21)
------------------

- In xhtml.addClassToLastChildren, do not define an empty class attribute.  Indeed, not
  managed tags were decorated with a 'class=""' attribute, this is no more the case.
  [gbastien]


0.4.8 (2015-04-20)
------------------

- Manage every text formatting tags in xhtml.addClassToLastChildren and
  do not break on unknwon tags.
  [gbastien]
- Replace special characters by corresponding HTML entity in xhtml.addClassToLastChildren
  so rendered content still contains original HTML entities.  This avoid HTML entities being
  rendered as UTF-8 characters and some weirdly recognized ("&nbsp;").
  [gbastien]


0.4.7 (2015-03-06)
------------------

- Adapted method xhtml.addClassToLastChildren to mark parent tag containing unhandled tags.
  [gbastien]


0.4.6 (2015-02-26)
------------------

- Added method markEmptyTags that will mark empty tags of a given
  xhtmlContent with a specific CSS class.
  [gbastien]
- Removed method security.call_as_super_user as we will rely on
  plone.api.env.adopt_roles to execute some methods as super user.
  [gbastien]


0.4.5 (2015-02-05)
------------------

- Added method to test if the buildout is in development mode (IS_DEV_ENV=True).
  [sgeulette]
- Added method to generate a password following criterias.
  [sgeulette]


0.4.4 (2015-01-29)
------------------

- Make it possible to pass specific class by tag to hxtml.addClassToLastChildren,
  this way, a specific class can be set depending on the node tag.
  [gbastien]


0.4.3 (2015-01-20)
------------------

- Added method addClassToLastChildren that will add a specific class attribute
  to last tags of a given xhtmlContent.
  [gbastien]


0.4.2 (2014-09-19)
------------------

- Do not consider xhtmlContent to easily empty : xhtmlContent is empty if it does not produce
  text, does not have attributes and does not have children.
  [gbastien]
- Use method xhtmlContentIsEmpty in method removeBlanks to avoid duplicating code and logic.
  [gbastien]

0.4.1 (2014-09-11)
------------------

- Corrected bug in 'removeBlanks' that removed children of an empty parent tag, that leaded
  to removal of complex trees like <u><li>My text</li><li>My second text</li></ul>.
  [gbastien]


0.3 (2014-09-04)
----------------

- Corrected bug in 'xhtmlContentIsEmpty' that did not managed correctly complex HTML tree.
  We use now lxml method 'text_content' to check if a HTML structure will render something or not.
  [gbastien]


0.2 (2014-08-27)
----------------

- Added xhtml.py module with helper methods for XHTML content :
    - 'removeBlanks' that will remove blank lines of a given xhtmlContent;
    - 'xhtmlContentIsEmpty' that will check if given xhtmlContent will produce something when rendered.

  [gbastien]

0.1 (2014-08-18)
----------------

- Initial release.
  [sdelcourt]
