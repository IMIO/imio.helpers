Changelog
=========

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
