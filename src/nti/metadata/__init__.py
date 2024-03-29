#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=global-statement

import six

from zope import component

from zope.catalog.interfaces import ICatalog
from zope.catalog.interfaces import INoAutoIndex

from zope.intid.interfaces import IIntIds

from nti.coremetadata.interfaces import IX_LASTSEEN_TIME

from nti.coremetadata.interfaces import IUser
from nti.coremetadata.interfaces import IRedisClient
from nti.coremetadata.interfaces import IContextLastSeenContainer

from nti.metadata.interfaces import INoMetadataAutoIndex

from nti.metadata.processing import add_metadata_to_queue
from nti.metadata.processing import add_user_lastseen_event_to_queue

from nti.zodb import isBroken

from nti.zope_catalog.interfaces import IDeferredCatalog

METADATA_CATALOG_NAME = 'nti.dataserver.++etc++metadata-catalog'

METADATA_QUEUE_NAME = '++etc++metadata++queue'

QUEUE_NAMES = (METADATA_QUEUE_NAME,)

REMOVED = 0
ADDED = 1
CHANGED = 2
MODIFIED = CHANGED
EVENT_TYPES = (REMOVED, CHANGED, ADDED)

logger = __import__('logging').getLogger(__name__)


def redis():
    return component.queryUtility(IRedisClient)


def is_indexable(obj):
    return not INoAutoIndex.providedBy(obj) \
       and not INoMetadataAutoIndex.providedBy(obj)


def metadata_catalogs():
    return tuple(component.getAllUtilitiesRegisteredFor(IDeferredCatalog))


def metadata_catalog():
    return component.queryUtility(ICatalog, name=METADATA_CATALOG_NAME)


# queue


def get_intids():
    return component.queryUtility(IIntIds)


def get_uid(obj, intids=None):
    intids = get_intids() if intids is None else intids
    return intids.queryId(obj) if intids is not None else None
get_iid = get_uid  # alias


def get_obj_uid(obj):
    if isinstance(obj, six.integer_types):
        doc_id = obj
    else:
        doc_id = get_uid(obj)
    return doc_id


def process_event(doc_id, event, ignore_errors=False):
    result = True
    intids = get_intids()
    catalogs = metadata_catalogs()
    try:
        if event is REMOVED:
            for catalog in catalogs:
                catalog.unindex_doc(doc_id)
        else:
            ob = intids.queryObject(doc_id)
            if ob is None:
                result = False
                logger.debug("Couldn't find object for %s", doc_id)
            elif isBroken(ob):
                result = False
                logger.warning("Ignoring broken object with id %s", doc_id)
            else:
                for catalog in catalogs:
                    if hasattr(catalog, 'force_index_doc'):
                        catalog.force_index_doc(doc_id, ob)
                    else:
                        catalog.index_doc(doc_id, ob)
    except Exception:  # pylint: disable=broad-except
        result = False
        if ignore_errors:
            logger.exception("Error while indexing object with id %s", doc_id)
        else:
            raise
    return result


def queue_metadata_event(obj, event):
    if redis() is None:
        return False
    doc_id = get_obj_uid(obj)
    if doc_id is not None:
        add_metadata_to_queue(QUEUE_NAMES[0], process_event, doc_id, event)
        return True
    return False
queue_event = queue_metadata_event # BWC


def queue_metadata_add(obj):
    queue_metadata_event(obj, ADDED)
queue_add = queue_metadata_add # BWC


def queue_metadata_modififed(obj):
    queue_metadata_event(obj, CHANGED)
queue_modififed = queue_metadata_modififed # BWC


def queue_metadata_removed(obj):
    queue_metadata_event(obj, REMOVED)
queue_removed = queue_metadata_removed # BWC


# users


def process_last_seen_event(doc_id, ignore_errors=True):
    result = True
    intids = get_intids()
    catalog = metadata_catalog()
    try:
        if catalog is not None and IX_LASTSEEN_TIME in catalog:
            obj = intids.queryObject(doc_id)
            if IUser.providedBy(obj):
                catalog[IX_LASTSEEN_TIME].index_doc(doc_id, obj)
    except Exception:  # pylint: disable=broad-except
        result = False
        if ignore_errors:
            logger.exception("Error while indexing user [%s] last seen ", doc_id)
        else:
            raise
    return result


def queue_user_last_seen_event(obj):
    doc_id = get_obj_uid(obj)
    if doc_id is not None:
        add_user_lastseen_event_to_queue(QUEUE_NAMES[0],
                                         process_last_seen_event,
                                         doc_id)
        return True
    return False
