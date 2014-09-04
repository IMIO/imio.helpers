Changelog
=========

0.4 (unreleased)
----------------

- Nothing changed yet.


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
