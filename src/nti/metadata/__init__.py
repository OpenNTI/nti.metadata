#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import time
import itertools

from zope import component

import zope.intid

from zope.catalog.interfaces import INoAutoIndex

from nti.dataserver import users
from nti.dataserver.interfaces import IUser
from nti.dataserver.interfaces import IMetadataCatalog
from nti.dataserver.metadata_index import CATALOG_NAME
from nti.dataserver.interfaces import IPrincipalMetadataObjectsIntIds

from nti.metadata.interfaces import IMetadataQueue
from nti.metadata.interfaces import DEFAULT_QUEUE_LIMIT

from nti.metadata.interfaces import IMetadataQueueFactory

def is_indexable(obj):
	return not INoAutoIndex.providedBy(obj)

def metadata_catalog():
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
	catalog = metadata_catalog()

	if queue is None:
		queue = metadata_queue()

	# Sync the queue if we have multiple instances running.
	if sync_queue and queue.syncQueue():
		logger.debug("Queue synced")
	queue_size = queue_length(queue)

	limit = queue_size if limit == -1 else limit
	to_process = min(limit, queue_size)
	if queue_size > 0:
		now = time.time()
		done = queue.process(ids, (catalog,), to_process, ignore_pke=ignore_pke)
		queue_size = max(0, queue_size-done)
		logger.info("%s event(s) processed in %s(s). Queue size %s", done, 
					time.time()-now, queue_size)

	return to_process

def get_principal_metadata_objects_intids(principal):
	predicates = component.subscribers((principal,), IPrincipalMetadataObjectsIntIds)
	for predicate in list(predicates):
		for uid in predicate.iter_intids():
			yield uid
