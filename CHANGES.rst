Changelog
=========

0.4.4 (unreleased)
------------------

- Make it possible to pass specific class by tag to hxtml.addClassToLastChildren,
  this way, a specific class can be set depending on the node tag.
  [gbastien]


0.4.3 (unreleased)
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
