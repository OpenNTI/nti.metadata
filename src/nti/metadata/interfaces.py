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

DEFAULT_QUEUE_LIMIT = 100

class IIndexReactor(interface.Interface):
	"""
	marker interface for a reactor
	"""

class IMetadataEventQueue(interface.Interface):
	pass

class IMetadataQueue(ICatalogQueue):

	buckets = interface.Attribute("number of event queues")

	def syncQueue():
		"""
		sync the length of this queue with its children event queues
		"""

	def eventQueueLength():
		"""
		return the length of all internal search event queues
		"""

	def __getitem__(idx):
		"""
		return the search event queue(s) for the specified index
		"""

class IMetadataQueueFactory(interface.Interface):
	"""
	A factory for metadata queues.
	"""
