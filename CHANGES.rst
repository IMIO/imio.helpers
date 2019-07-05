Changelog
=========

0.19 (2019-07-05)
-----------------

- Patch index method from collective.solr to fix an issue with partial reindex
  [mpeeters]
- Added css id on row field display in container.pt and content.pt.
  [sgeulette]

0.18 (2019-05-16)
-----------------

- Added `appy.pod` sample that show problem of wrongly defined style like
  `margin-left: opt;` using `opt` instead `0pt`.
  [gbastien]
- Added `appy.pod` sample that show problem of class not used in `<li>`
  or `<td>`.
  [gbastien]
- Added methods `content.disable_link_integrity_checks` and
  `content.restore_link_integrity_checks` to be able to disable the
  `enable_link_integrity_checks property` and to restore it to it's original
  value.  This works for Plone4 (property) and Plone5 (registry).
  [gbastien]
- Fix import of `IEditingSchema` on Plone5.
  [gbastien]

0.17 (2019-02-12)
-----------------

- Added collapsible option on container view.
  [sgeulette]
- Do not store date for get_cachekey_volatile/invalidate_cachekey_volatile_for
  in a volatile (_v_...) as it seems "stored" by thread and is computed to much
  times.
  [gbastien]
- Added JS helper method has_faceted returning true if currently on a faceted.
  [gbastien]

0.16 (2019-01-31)
-----------------

- Added `appy.pod` usecase to show problems with table optimization if
  `<td>` has a defined size.
  [gbastien]
- Added `appy.pod` usecase to show problems with table having a first empty
  `<tr></tr>` that do not render second column of following lines.
  [gbastien]
- Added `appy.pod` usecase for line-height style.
  [gbastien]
- Added `appy.pod` usecase for `<img>` without `src` that breaks generation.
  [gbastien]
- Do not break in `xhtml.imagesToPath` if `<img>` does not have a `src`.
  [gbastien]

0.15 (2018-12-18)
-----------------

- Display more logging in `content.validate_fields` when bypassing validation.
  [gbastien]
- In `catalog.addOrUpdateIndexes`, pass a `ZLogHandler` to `reindexIndex` so the
  progress is shown in the Zope log.
  [gbastien]
- In `content.add_to_annotation` and `content.del_from_annotation`, store
  annotation in a `PersistentList` instead a `set()` to avoid persistence
  problems.
  [gbastien]

0.14 (2018-10-22)
-----------------

- Improved content create to avoid creating object when defined id already exists.
  [sgeulette]
- Added methods content.uuidsToCatalogBrains and content.uuidsToObjects.
  [gbastien]
- Adapted `content.validate_fields` to bypass validation when field.required=False,
  value is None and field type is other than Bool.  Validation is also bypassed for
  field using a `source` attribute because it fails for now...
  [gbastien]
- Added parameter raise_on_errors to content.validate_fields to raise a ValueError
  when errors are found instead simply returning it.
  [gbastien]

0.13 (2018-08-31)
-----------------

- Added `content.get_schema_fields` to get schema fields (behaviors included
  by default).
  [sgeulette]
- Pep8 on imports.
  [sgeulette]
- Added appy.pod usecase for lists containing tables.
  [bleybaert]
- Added dependency on `Plone` in `setup.py`.
  [gbastien]
- Do not break in `xhtml.storeImagesLocally._handle_internal_image` if image
  src is not a path to an image but to another element (like `Folder` or
  `Plone Site`).
  [gbastien]

0.12 (2018-05-03)
-----------------

- Added appy.pod usecase for rgba().
  [gbastien]
- Improved annotation code
  [sgeulette]

0.11 (2018-01-30)
-----------------

- Use `html` instead `xml` for `lxml.html.to_string` rendering `method`.
  This avoids results like `<p><s></s></p>` turned to `<p><s/></p>`.
  [gbastien]

0.10 (2017-12-21)
-----------------

- Fixed bug in `catalog.addOrUpdateIndexes` where a new index was not reindexed
  if it was added together with an already existing index.
  [gbastien]
- Fixed bug in `xhtml.storeImagesLocally` when img uses a `resolveuid` and
  starts with the `portal_url` (this is the case when using `uploadimage plugin`
  in `collective.ckeditor`), it raised a NotFound error.
  [gbastien]
- In `xhtml.storeImagesLocally`, keep the `scale` at the end of the URL using
  `resolveuid` (like `resolveuid/content_uid/image_preview`).
  [gbastien]
- Use `PyPDF2` instead deprecated `pyPdf` to insert barcode into PDF.
  This solves `ValueError: invalid literal for int() with base 10: ''`.
  [gbastien]

0.9 (2017-11-27)
----------------

- Added appy.pod usecase for complex styles start/end on same paragraph.
  [gbastien]
- Do not break in `xhtml.storeImagesLocally` when no `<img> src` found.
  [gbastien]
- Add methods to manage annotations (Add and Remove).
  [anuyens, odelaere]
- Added method to get annotation
  [sgeulette]

0.8 (2017-10-04)
----------------

- In `xhtml.storeImagesLocally`, take into account `<img> src`
  that uses `resolveuid`.  This is the case when using `collective.ckeditor` and
  option `allow_link_byuid` is enabled.
  [gbastien]
- Do not use `/* ... */` together with `https://` in helpers.js comment or
  merged javascripts produce a wrong format and raise a JS comment unterminated
  error in the browser.
  [gbastien]

0.7 (2017-09-22)
----------------

- Added method `testing_logger` to `testing.py` that enables logging into tests.
  [gbastien]

0.6 (2017-09-15)
----------------

- Changed method `xhtml.storeExternalImagesLocally` to
  `xhtml.storeImagesLocally`, it handles now external and internal images
  retrieval so an image stored in the portal is also created in given context
  when necessary.
  [gbastien]

0.5 (2017-08-30)
----------------

- Added method to safe encode string.
  [sgeulette]
- appy.pod usecase : table using width of 0px.
  [gbastien]
- In `content.validate_fields`, added special bypass to avoid failing
  validation for `Choice` field that is `required=False` and for which given
  value is None. Validation fails because None not in vocabulary but it is
  nevertheless a correct value as it is managed by the widget while added thru
  the UI.
  [gbastien]
- Added JS fix to be able to print `<fieldset>` on several pages in Firefox,
  see https://bugzilla.mozilla.org/show_bug.cgi?id=471015.
  This makes it necessary to add a default profile to add the JS resource
  `++resource++imio.helpers/helpers.js`.
  [gbastien]

0.4.29 (2017-07-25)
-------------------

- Get intid value or create it if not found.
  [sgeulette]
- Added possibility to pass 'scale' value to pdf.BarcodeStamp.
  [gbastien]
- More appy.pod usecase : not rendered sub bullets with no parent bullet.
  [gbastien]

0.4.28 (2017-07-04)
-------------------

- Added method to create NamedBlobFile or NamedBlobImage.
  [sgeulette]

0.4.27 (2017-06-30)
-------------------

- Return portal when obj_path is / on create content.
  [bsuttor]
- Added case for appy.pod that show complex HTML structure failing
  in appy.pod 0.9.7.
  [gbastien]
- Added root attribute in fancytree
  [sgeulette]
- Changed barcode generation options, following zint 2.6
  [sgeulette]

0.4.26 (2017-03-14)
-------------------

- Set CLASS_TO_LAST_CHILDREN_NUMBER_OF_CHARS_DEFAULT = 240.
  [gbastien]

0.4.25 (2017-02-21)
-------------------

- Use same class names than appy.pod regarding the 'keep with next'
  functionnality.
  [gbastien]

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
