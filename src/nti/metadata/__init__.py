#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import time

from zope import component

from zope.catalog.interfaces import INoAutoIndex

from zope.intid.interfaces import IIntIds

from nti.dataserver.interfaces import IPrincipalMetadataObjects

from nti.dataserver.metadata_index import CATALOG_NAME

from nti.metadata.interfaces import NO_QUEUE_LIMIT
from nti.metadata.interfaces import DEFAULT_QUEUE_LIMIT as QUEUE_LIMIT

from nti.metadata.interfaces import IMetadataQueueFactory

from nti.zodb import isBroken

from nti.zope_catalog.interfaces import IMetadataCatalog

def is_indexable(obj):
	return not INoAutoIndex.providedBy(obj)

def metadata_catalogs():
	return tuple(catalog for _, catalog in component.getUtilitiesFor(IMetadataCatalog))

def dataserver_metadata_catalog():
	return component.queryUtility(IMetadataCatalog, name=CATALOG_NAME)

def metadata_queue():
	factory = component.getUtility(IMetadataQueueFactory)
	return factory.get_queue()

def queue_length(queue=None):
	queue = queue if queue is not None else metadata_queue()
	try:
		result = len(queue)
	except ValueError:
		result = 0
		logger.error("Could not compute queue length")
	return result

def process_queue(limit=QUEUE_LIMIT, sync_queue=True, queue=None, ignore_pke=True):
	ids = component.getUtility(IIntIds)
	catalogs = metadata_catalogs()
	queue = metadata_queue() if queue is None else queue

	# Sync the queue if we have multiple instances running.
	if sync_queue and queue.syncQueue():
		logger.debug("Queue synced")
	queue_size = queue_length(queue)

	limit = queue_size if limit == NO_QUEUE_LIMIT else limit
	to_process = min(limit, queue_size)
	if queue_size > 0:
		now = time.time()
		done = queue.process(ids, catalogs, to_process, ignore_pke=ignore_pke)
		queue_size = max(0, queue_size - done)
		logger.info("%s event(s) processed in %s(s). Queue size %s", done,
					time.time() - now, queue_size)

	return to_process

def get_uid(obj, intids=None):
	intids = component.getUtility(IIntIds) if intids is None else intids
	if not isBroken(obj):
		uid = intids.queryId(obj)
		if uid is None:
			logger.warn("Ignoring unregistered object %s", obj)
		else:
			return uid
	return None
get_iid = get_uid  # alias

def get_principal_metadata_objects(principal):
	predicates = component.subscribers((principal,), IPrincipalMetadataObjects)
	for predicate in list(predicates):
		for obj in predicate.iter_objects():
			if not isBroken(obj):
				yield obj

def get_principal_metadata_objects_intids(principal):
	intids = component.getUtility(IIntIds)
	for obj in get_principal_metadata_objects(principal):
		uid = get_uid(obj, intids=intids)
		if uid is not None:
			yield uid
