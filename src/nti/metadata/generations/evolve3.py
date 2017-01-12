#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
generation 3.

.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

generation = 3

from zope import component

from zope.component.hooks import site
from zope.component.hooks import setHooks

from zope.intid.interfaces import IIntIds

from nti.zope_catalog.interfaces import IMetadataCatalog

from nti.dataserver.metadata_index import CATALOG_NAME
from nti.dataserver.metadata_index import IX_SHAREDWITH
from nti.dataserver.metadata_index import IX_REVSHAREDWITH
from nti.dataserver.metadata_index import RevSharedWithIndex

from nti.metadata import metadata_queue


def do_evolve(context):
    setHooks()
    conn = context.connection
    root = conn.root()
    ds_folder = root['nti.dataserver']

    lsm = ds_folder.getSiteManager()
    intids = lsm.getUtility(IIntIds)

    total = 0
    with site(ds_folder):
        assert   component.getSiteManager() == ds_folder.getSiteManager(), \
                "Hooks not installed?"

        catalog = lsm.getUtility(provided=IMetadataCatalog, name=CATALOG_NAME)

        sharedWithIdx = catalog[IX_SHAREDWITH]
        try:
            index = catalog[IX_REVSHAREDWITH]
        except KeyError:
            index = RevSharedWithIndex(family=intids.family)
            intids.register(index)
            index.__parent__ = catalog
            index.__name__ = IX_REVSHAREDWITH
            catalog[IX_REVSHAREDWITH] = index

        queue = metadata_queue()
        if queue is None:
            return None

        for uid in sharedWithIdx.ids():
            try:
                queue.add(uid)
                total += 1
            except TypeError:
                pass

        logger.info('Metadata evolution %s done; %s object(s) put in queue',
                    generation, total)

    return total


def evolve(context):
    """
    Evolve to generation 3 by adding a revSharedWith index
    """
    do_evolve(context)
