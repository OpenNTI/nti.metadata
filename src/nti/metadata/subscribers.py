#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component
from zope import interface

from zope.intid.interfaces import IIntIds
from zope.intid.interfaces import IIntIdAddedEvent
from zope.intid.interfaces import IIntIdRemovedEvent

from zope.lifecycleevent.interfaces import IObjectRemovedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

from nti.dataserver.interfaces import IEntity

from nti.dataserver.metadata_index import IX_CREATOR
from nti.dataserver.metadata_index import IX_TAGGEDTO
from nti.dataserver.metadata_index import IX_SHAREDWITH
from nti.dataserver.metadata_index import IX_REVSHAREDWITH
from nti.dataserver.metadata_index import IX_REPLIES_TO_CREATOR

from nti.metadata import is_indexable
from nti.metadata import metadata_queue
from nti.metadata import dataserver_metadata_catalog

from nti.zope_catalog.interfaces import IKeywordIndex

def query_uid(obj):
	intids = component.queryUtility(IIntIds)
	attribute = getattr(intids, 'attribute', '_ds_intid')
	result = getattr(obj, attribute, None)
	# Fall back to our utility if we need to.
	# Extremely slow if we do __len__
	if result is None and intids is not None:
		result = intids.queryId(obj)
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
@component.adapter(interface.Interface, IIntIdRemovedEvent)
def _object_removed(modeled, event):
	queue_remove(modeled)

# IIntIdAddedEvent
@component.adapter(interface.Interface, IIntIdAddedEvent)
def _object_added(modeled, event):
	queue_added(modeled)

# IObjectModifiedEvent
@component.adapter(interface.Interface, IObjectModifiedEvent)
def _object_modified(modeled, event):
	queue_modified(modeled)

def delete_entity_data(username):
	result = 0
	logger.info("Removing metadata data for user %s", username)
	catalog = dataserver_metadata_catalog()
	if catalog is not None:
		username = username.lower()
		index = catalog[IX_CREATOR]
		query = {IX_CREATOR: {'any_of': (username,)} }
		results = catalog.searchResults(**query)
		for uid in results.uids:
			index.unindex_doc(uid)
			result += 1
	return result

@component.adapter(IEntity, IObjectRemovedEvent)
def _on_entity_removed(entity, event):
	username = entity.username
	delete_entity_data(username)

@component.adapter(IEntity, IObjectRemovedEvent)
def clear_replies_to_creator_when_creator_removed(entity, event):
	"""
	When a creator is removed, all of the things that were direct
	replies to that creator are now \"orphans\", with a value
	for ``inReplyTo``. We clear out the index entry for ``repliesToCreator``
	for this entity in that case.

	The same scenario holds for things that were shared directly
	to that user.
	"""

	catalog = dataserver_metadata_catalog()
	if catalog is None:
		# Not installed yet
		return

	# These we can simply remove, this creator doesn't exist anymore
	for ix_name in (IX_REPLIES_TO_CREATOR, IX_TAGGEDTO):
		index = catalog[ix_name]
		query = {ix_name: {'any_of': (entity.username,)} }
		results = catalog.searchResults(**query)
		for uid in results.uids:
			index.unindex_doc(uid)

	# These, though, may still be shared, so we need to reindex them
	index = catalog[IX_SHAREDWITH]
	results = catalog.searchResults(sharedWith={'all_of': (entity.username,)})
	intid_util = results.uidutil
	uids = list(results.uids or ())
	for uid in uids:
		obj = intid_util.queryObject(uid)
		if obj is not None:
			index.index_doc(uid, obj)

	index = catalog[IX_REVSHAREDWITH]
	if IKeywordIndex.providedBy(index):
		index.remove_words((entity.username,))
