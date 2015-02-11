#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import time

import zope.intid

from zope import component
from zope.catalog.interfaces import INoAutoIndex

from ZODB.interfaces import IBroken
from ZODB.POSException import POSError

from nti.dataserver import users

from nti.dataserver.interfaces import IUser
from nti.dataserver.interfaces import IMetadataCatalog
from nti.dataserver.interfaces import IPrincipalMetadataObjects

from nti.dataserver.metadata_index import CATALOG_NAME

from nti.metadata.interfaces import IMetadataQueue
from nti.metadata.interfaces import DEFAULT_QUEUE_LIMIT

from nti.metadata.interfaces import IMetadataQueueFactory

def is_indexable(obj):
	return not INoAutoIndex.providedBy(obj)

def metadata_catalogs():
	result = [catalog for _, catalog in component.getUtilitiesFor(IMetadataCatalog)]
	return result

def dataserver_metadata_catalog():
	result = component.queryUtility(IMetadataCatalog, name=CATALOG_NAME)
	return result

def metadata_queue():
	factory = component.getUtility(IMetadataQueueFactory)
	result = factory.get_queue()
	return result

def queue_length(queue=None):
	queue = queue if queue is not None else metadata_queue()
	try:
		result = len(queue)
	except ValueError:
		result = 0
		logger.error("Could not compute queue length")
	return result

def process_queue(limit=DEFAULT_QUEUE_LIMIT, sync_queue=True, queue=None,
				  ignore_pke=True):

	ids = component.getUtility(zope.intid.IIntIds)
	catalogs = metadata_catalogs()
	queue = metadata_queue() if queue is None else queue

	# Sync the queue if we have multiple instances running.
	if sync_queue and queue.syncQueue():
		logger.debug("Queue synced")
	queue_size = queue_length(queue)

	limit = queue_size if limit == -1 else limit
	to_process = min(limit, queue_size)
	if queue_size > 0:
		now = time.time()
		done = queue.process(ids, catalogs, to_process, ignore_pke=ignore_pke)
		queue_size = max(0, queue_size-done)
		logger.info("%s event(s) processed in %s(s). Queue size %s", done, 
					time.time()-now, queue_size)

	return to_process

def get_uid(obj, intids=None):
	intids = component.getUtility(zope.intid.IIntIds) if intids is None else intids
	try:
		if IBroken.providedBy(obj):
			logger.warn("ignoring broken object %s", type(obj))
		elif obj is not None:
			uid = intids.queryId(obj)
			if uid is None:
				logger.warn("ignoring unregistered object %s", obj)
			else:
				return uid
	except (TypeError, POSError):
		logger.error("ignoring broken object %s", type(obj))
	return None
get_iid = get_uid # alias

def get_principal_metadata_objects(principal):
	predicates = component.subscribers((principal,), IPrincipalMetadataObjects)
	for predicate in list(predicates):
		for obj in predicate.iter_objects():
			try:
				if obj is None:
					continue
				elif IBroken.providedBy(obj):
					logger.warn("ignoring broken object %s", type(obj))
				else:
					yield obj
			except (TypeError, POSError):
				logger.error("ignoring broken object %s", type(obj))
			
def get_principal_metadata_objects_intids(principal):
	intids = component.getUtility(zope.intid.IIntIds) 
	for obj in get_principal_metadata_objects(principal):
		uid = get_uid(obj, intids=intids)
		if uid is not None: 
			yield uid
