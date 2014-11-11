#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import gevent
from functools import partial

import zope.intid

from zope import component
from zope.lifecycleevent import IObjectRemovedEvent

import transaction

from nti.dataserver.interfaces import IEntity
from nti.dataserver.interfaces import IDataserverTransactionRunner

from nti.dataserver.metadata_index import IX_CREATOR

from . import is_indexable
from . import metadata_queue
from . import metadata_catalog

def query_uid( obj ):
	intids = component.queryUtility( zope.intid.IIntIds )
	result = getattr( obj, '_ds_intid', None )
	## Fall back to our utility if we need to.
	## Extremely slow if we do __len__
	if result is None and intids is not None:
		result = intids.queryId( obj )
	return result

def add_2_queue(obj):
	iid = query_uid(obj)
	if iid is not None:
		__traceback_info__ = iid
		queue = metadata_queue()
		if queue is not None:
			queue.add(iid)
			return True
	return False

def queue_added(obj):
	if is_indexable(obj):
		try:
			return add_2_queue(obj)
		except TypeError:
			pass
	return False

def queue_modified(obj):
	if is_indexable(obj):
		iid = query_uid(obj)
		if iid is not None:
			__traceback_info__ = iid
			try:
				queue = metadata_queue()
				if queue is not None:
					queue.update(iid)
					return True
			except TypeError:
				pass
	return False

def queue_remove(obj):
	if is_indexable(obj):
		iid = query_uid(obj)
		if iid is not None:
			__traceback_info__ = iid
			queue = metadata_queue()
			if queue is not None:
				queue.remove(iid)

# IIntIdRemovedEvent
def _object_removed(modeled, event):
	queue_remove(modeled)

# IIntIdAddedEvent
def _object_added(modeled, event):
	queue_added(modeled)

# IObjectModifiedEvent
def _object_modified(modeled, event):
	queue_modified(modeled)

def delete_entity_data(username):
	logger.info("Removing metadata data for user %s", username)
	result = 0
	queue = metadata_queue()
	catalog = metadata_catalog()
	if queue is not None and catalog is not None:
		username = username.lower()
		query = {IX_CREATOR: {'any_of': (username,)} }
		results = catalog.searchResults(**query)
		for uid in results.uids:
			queue.remove(uid)
			result +=1
	return result
	
@component.adapter(IEntity, IObjectRemovedEvent)
def _on_entity_removed(entity, event):
	username = entity.username
	def _process_event():
		transaction_runner = \
			component.getUtility(IDataserverTransactionRunner)
		func = partial(delete_entity_data, username=username)
		transaction_runner(func)
		return True

	transaction.get().addAfterCommitHook(
					lambda success: success and gevent.spawn(_process_event))
