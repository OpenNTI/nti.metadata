#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

generation = 6

from zope import component
from zope import interface

from zope.component.hooks import setHooks
from zope.component.hooks import site as current_site

from zope.intid.interfaces import IIntIds

from nti.dataserver.interfaces import IDataserver
from nti.dataserver.interfaces import IOIDResolver

from nti.metadata import queue_add

from nti.metadata.interfaces import IMetadataQueue


@interface.implementer(IDataserver)
class MockDataserver(object):

    root = None

    def get_by_oid(self, oid, ignore_creator=False):
        resolver = component.queryUtility(IOIDResolver)
        if resolver is None:
            logger.warn("Using dataserver without a proper ISiteManager.")
        else:
            return resolver.get_object_by_oid(oid, ignore_creator=ignore_creator)
        return None


def do_evolve(context, generation=generation):
    setHooks()
    conn = context.connection
    ds_folder = conn.root()['nti.dataserver']

    mock_ds = MockDataserver()
    mock_ds.root = ds_folder
    component.provideUtility(mock_ds, IDataserver)

    lsm = ds_folder.getSiteManager()
    intids = lsm.getUtility(IIntIds)
    with current_site(ds_folder):
        assert  component.getSiteManager() == ds_folder.getSiteManager(), \
                "Hooks not installed?"

        meta_queue = lsm.queryUtility(provided=IMetadataQueue)
        if meta_queue is not None:
            intids.unregister(meta_queue)
            lsm.unregisterUtility(meta_queue, provided=IMetadataQueue)
            try:
                for queue in meta_queue._queues or ():
                    for uid, event in queue._data.items():
                        queue_add(uid, event)
                    queue._data.clear()
                # reset
                meta_queue._reset(0)
            except AttributeError:
                pass

    component.getGlobalSiteManager().unregisterUtility(mock_ds, IDataserver)
    logger.info('Metadata evolution %s done', generation)
        

def evolve(context):
    """
    Evolve to generation 6 by moving metata processing to redis
    """
    do_evolve(context, generation)
