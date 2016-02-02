#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from zc.catalogqueue.interfaces import ICatalogQueue

#: Default process queue limit
DEFAULT_QUEUE_LIMIT = 100

class IIndexReactor(interface.Interface):
	"""
	marker interface for a reactor
	"""

class IMetadataEventQueue(interface.Interface):
	pass

class IMetadataQueue(ICatalogQueue):

	buckets = interface.Attribute("number of event queues")

	def extend(ids):
		"""
		Helper method to add the specified iterable of ids
		"""

	def syncQueue():
		"""
		Sync the length of this queue with its children event queues
		"""

	def eventQueueLength():
		"""
		Return the length of all internal search event queues
		"""

	def __getitem__(idx):
		"""
		Return the search event queue(s) for the specified index
		"""

class IMetadataQueueFactory(interface.Interface):
	"""
	A factory for metadata queues.
	"""
