#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import itertools

from zope import component

import zope.intid

from zope.catalog.interfaces import INoAutoIndex

from nti.dataserver import users
from nti.dataserver.interfaces import IUser

from nti.dataserver.metadata_index import CATALOG_NAME

from nti.zope_catalog.interfaces import IMetadataCatalog
from nti.metadata.interfaces import IMetadataQueue
from nti.metadata.interfaces import DEFAULT_QUEUE_LIMIT

from nti.metadata.interfaces import IMetadataQueueFactory

LOCK_NAME = str( "nti/metadata/lock" )

def is_indexable(obj):
	return not INoAutoIndex.providedBy( obj )

def metadata_catalog():
	result = component.getUtility(IMetadataCatalog, name=CATALOG_NAME)
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

def process_queue(limit=DEFAULT_QUEUE_LIMIT, sync_queue=True, queue=None):
	# TODO sync_queue?
	ids = component.getUtility(zope.intid.IIntIds)
	catalog = metadata_catalog()

	if queue is None:
		queue = metadata_queue()
	if sync_queue and queue.syncQueue():
		logger.debug("Queue synced")
	queue_size = queue_length(queue)

	limit = queue_size if limit == -1 else limit
	to_process = min(limit, queue_size)
	if queue_size > 0:
		logger.info("Taking %s event(s) to process; current queue size %s",
					to_process, queue_size)
		queue.process(ids, (catalog,), to_process)

	return to_process
