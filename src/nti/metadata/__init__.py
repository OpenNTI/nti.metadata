#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import six
import time

from zope import component

from zope.catalog.interfaces import INoAutoIndex

from zope.intid.interfaces import IIntIds

from nti.coremetadata.interfaces import IRedisClient

from nti.metadata.interfaces import INoMetadataAutoIndex
from nti.metadata.interfaces import IMetadataQueueFactory

from nti.metadata.processing import add_to_queue

from nti.zodb import isBroken

from nti.zope_catalog.interfaces import IMetadataCatalog

QUEUE_NAMES = ('++etc++metadata++queue',)

REMOVED = 0
ADDED = 1
CHANGED = 2
MODIFIED = CHANGED
EVENT_TYPES = (REMOVED, CHANGED, ADDED)


_redis = None
def redis():
    global _redis
    if _redis is None:
        _redis = component.queryUtility(IRedisClient)
    return _redis


def is_indexable(obj):
    return  not INoAutoIndex.providedBy(obj) \
        and not INoMetadataAutoIndex.providedBy(obj)


def metadata_catalogs():
    return tuple(component.getAllUtilitiesRegisteredFor(IMetadataCatalog))


# queue


def get_uid(obj, intids=None):
    intids = component.queryUtility(IIntIds) if intids is None else intids
    return intids.queryId(obj) if intids is not None else None
get_iid = get_uid  # alias


def process_event(doc_id, event, ignore_errors=True):
    catalogs = metadata_catalogs()
    intids = component.getUtility(IIntIds)
    try:
        if event is REMOVED:
            for catalog in catalogs:
                catalog.unindex_doc(doc_id)
        else:
            ob = intids.queryObject(doc_id)
            if ob is None:
                logger.debug("Couldn't find object for %s", doc_id)
            elif isBroken(ob):
                logger.warn("Ignoring broken object with id %s", doc_id)
            else:
                for catalog in catalogs:
                    if IMetadataCatalog.providedBy(catalog):
                        catalog.force_index_doc(doc_id, ob)
                    else:
                        catalog.index_doc(doc_id, ob)
    except Exception:
        if ignore_errors:
            logger.exception("Error while indexing object with id %s", id)
        else:
            raise


def queue_event(obj, event):
    if redis() is None:
        return
    if isinstance(obj, six.integer_types):
        doc_id = obj
    else:
        doc_id = get_uid(obj)
    if doc_id is not None:
        add_to_queue(QUEUE_NAMES[0], process_event, doc_id, event)


def queue_add(obj):
    queue_event(obj, ADDED)


def queue_modififed(obj):
    queue_event(obj, CHANGED)


def queue_removed(obj):
    queue_event(obj, REMOVED)
