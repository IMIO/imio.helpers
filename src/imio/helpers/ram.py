# -*- coding: utf-8 -*-

from DateTime import DateTime
from plone import api
from six.moves.cPickle import dumps
from time import time
from zope.globalrequest import getRequest
from zope.ramcache.ram import caches
from zope.ramcache.ram import RAMCache
from zope.ramcache.ram import Storage
from zope.ramcache.ram import writelock


class IMIORAMCache(RAMCache):
    """ """

    def _getStorage(self):
        """Finds or creates a storage object."""
        cacheId = self._cacheId
        with writelock:
            if cacheId not in caches:
                # imio.helpers, only changed here, use IMIOStorage instead Storage
                caches[cacheId] = IMIOStorage(
                    self.maxEntries, self.maxAge, self.cleanupInterval)
            return caches[cacheId]


class IMIOStorage(Storage):
    """ """

    def getEntry(self, ob, key):
        if self.lastCleanup <= time() - self.cleanupInterval:
            self.cleanup()

        try:
            data = self._data[ob][key]
        except KeyError:
            if ob not in self._misses:
                self._misses[ob] = 0
            self._misses[ob] += 1
            raise
        else:
            data[2] += 1                    # increment access count
            # XXX begin change by imio.helpers, update timestamp
            timestamp = time()
            data[1] = timestamp
            # XXX end change by PM

            return data[0]

    def getStatistics(self):
        objects = self._data.keys()
        objects.sort()
        result = []

        for ob in objects:
            try:
                size = len(dumps(self._data[ob]))
            except Exception as exc:
                size = 0
                api.portal.show_message(
                    'Could not compute size for "%s", original exception was "%s"'
                    % (repr(ob), repr(exc)), request=getRequest())
            hits = sum(entry[2] for entry in self._data[ob].itervalues())
            older_date = min(entry[1] for entry in self._data[ob].itervalues())
            result.append({'path': ob,
                           'hits': hits,
                           'misses': self._misses.get(ob, 0),
                           'size': size,
                           'entries': len(self._data[ob]),
                           'older_date': older_date and DateTime(older_date)})
        return tuple(result)


# instantiate our RAM Cache
imio_global_cache = IMIORAMCache()
