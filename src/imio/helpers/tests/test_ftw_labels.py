# -*- coding: utf-8 -*-

from imio.helpers import HAS_FTW_LABELS
from imio.helpers.testing import IntegrationTestCase
from imio.helpers.tests.utils import require_module
from plone import api
from zope.interface import alsoProvides


if HAS_FTW_LABELS:
    from ftw.labels.interfaces import ILabelJar
    from ftw.labels.interfaces import ILabelRoot
    from ftw.labels.interfaces import ILabelSupport


class TestFtwLabels(IntegrationTestCase):

    def test_dummy_ftw_labels(self):
        """Avoid "TypeError: Module imio.helpers.tests.test_ftw_labels does not define any tests"
           whhen tests are executed without ftw.labels."""
        pass

    @require_module("ftw.labels")
    def test_labels_indexer(self):
        """ """
        # make portal a label jar
        alsoProvides(self.portal, ILabelRoot)
        obj = api.content.create(
            container=self.portal.folder,
            id="mydoc",
            title="My document",
            type="Document")
        alsoProvides(obj, ILabelSupport)
        obj.reindexObject(idxs=['labels'])
        # create one personal and one global label in the jar
        jar = ILabelJar(obj)
        jar.add(title="My personal label", color="green", by_user=True)
        jar.add(title="My global label", color="blue", by_user=False)
        # for now, no label on obj
        index = self.catalog.Indexes['labels']
        rid = self.catalog(UID=obj.UID())[0].getRID()
        self.assertEqual(index.getEntryForObject(rid), ['__empty_string__', '_'])
        # add a personal label
        view = obj.restrictedTraverse('@@labeling')
        self.request.form['label_id'] = 'my-personal-label'
        self.request.form['active'] = 'False'
        view.pers_update()
        # still marked as having no global label
        self.assertEqual(
            index.getEntryForObject(rid),
            ['__empty_string__',
             'my-personal-label',
             'test_user_1_:my-personal-label'])
        # add a global label
        self.request.form['activate_labels'] = ['my-global-label']
        view.update()
        # no more marked as having no global label
        self.assertEqual(
            index.getEntryForObject(rid),
            ['my-global-label',
             'my-personal-label',
             'test_user_1_:my-personal-label'])
