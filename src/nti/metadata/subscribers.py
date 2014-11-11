#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division

__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import zope.intid

from zope import component
from zope.lifecycleevent import IObjectRemovedEvent

from nti.dataserver.interfaces import IEntity
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

@component.adapter(IEntity, IObjectRemovedEvent)
def _on_entity_removed(entity, event):
	queue = metadata_queue()
	catalog = metadata_catalog()
	if catalog is None or queue is None:
		return

	query = {IX_CREATOR: {'any_of': (entity.username,)} }
	results = catalog.searchResults(**query)
	for uid in results.uids:
		queue.remove(uid)
