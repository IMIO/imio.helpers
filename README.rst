.. image:: https://github.com/IMIO/imio.helpers/actions/workflows/main.yml/badge.svg?branch=master
    :target: https://github.com/IMIO/imio.helpers/actions/workflows/main.yml

.. image:: https://coveralls.io/repos/IMIO/imio.helpers/badge.png?branch=master
   :target: https://coveralls.io/r/IMIO/imio.helpers?branch=master

.. image:: http://img.shields.io/pypi/v/imio.helpers.svg
   :alt: PyPI badge
   :target: https://pypi.org/project/imio.helpers


====================
imio.helpers
====================

Various helper methods for development.


Requirements
------------

The barcode generation method uses zint tool (https://sourceforge.net/projects/zint/).

You have to install zint version >= 2.6.0.


Caching
-------

Use cache.get_plone_groups_for_user(the_objects=True) instead portal_groups.getGroupsForPrincipal
Avoid portal_groups.getGroupById but use source_groups.get
