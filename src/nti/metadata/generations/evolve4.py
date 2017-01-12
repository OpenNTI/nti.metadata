#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
generation 4.

.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

generation = 4

from zope import component

from zope.component.hooks import site
from zope.component.hooks import setHooks

from nti.zope_catalog.interfaces import IMetadataCatalog

from nti.dataserver.metadata_index import IX_MIMETYPE
from nti.dataserver.metadata_index import CATALOG_NAME

from nti.metadata import metadata_queue

PERSONAL_BLOG_ENTRY_POST = 'application/vnd.nextthought.forums.personalblogentrypost'


def do_evolve(context, generation=generation):
    setHooks()
    conn = context.connection
    root = conn.root()
    ds_folder = root['nti.dataserver']

    lsm = ds_folder.getSiteManager()

    total = 0
    with site(ds_folder):
        assert  component.getSiteManager() == ds_folder.getSiteManager(), \
                "Hooks not installed?"

        catalog = lsm.getUtility(provided=IMetadataCatalog, name=CATALOG_NAME)
        doc_ids = catalog[IX_MIMETYPE].apply(
            {'any_of': (PERSONAL_BLOG_ENTRY_POST,)})

        queue = metadata_queue()
        if queue is not None:
            for uid in doc_ids or ():
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
    Evolve to generation 4 by reindexing all personal entry blogs
    """
    do_evolve(context)
