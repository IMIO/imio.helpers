# -*- coding: utf-8 -*-

import pkg_resources

try:
    pkg_resources.get_distribution("collective.solr")
except pkg_resources.DistributionNotFound:
    HAS_SOLR = False
else:
    from collective.solr.indexer import SolrIndexProcessor

    HAS_SOLR = True


def solr_index(self, obj, attributes=None):
    # Fix issue https://github.com/collective/collective.solr/issues/189
    if attributes is not None:
        attributes = None
    return SolrIndexProcessor._old_index(self, obj, attributes)
