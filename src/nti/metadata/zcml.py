#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
Directives to be used in ZCML

$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface
from zope import component
from zope.component.zcml import utility

from nti.metadata import process_queue

from nti.metadata.interfaces import IMetadataQueue
from nti.metadata.interfaces import IMetadataQueueFactory

class ImmediateQueueRunner(object):

	def add(self, id):
		# Process immediately
		queue = component.getUtility(IMetadataQueue)
		queue.add( id )
		process_queue( queue=queue )

@interface.implementer(IMetadataQueueFactory)
class _ImmediateQueueFactory(object):

	def get_queue( self, name ):
		return ImmediateQueueRunner()

@interface.implementer(IMetadataQueueFactory)
class _ProcessingQueueFactory(object):

	def get_queue( self, name ):
		queue = component.getUtility(IMetadataQueue)
		if queue is None:
			raise ValueError("No queue exists for metadata processing queue (%s). "
							 "Evolve error?" % name )
		return queue

def registerImmediateProcessingQueue(_context):
	logger.info( "Registering immediate processing queue" )
	factory = _ImmediateQueueFactory()
	utility( _context, provides=IMetadataQueueFactory, component=factory)

def registerProcessingQueue(_context):
	logger.info( "Registering processing queue" )
	factory = _ProcessingQueueFactory()
	utility( _context, provides=IMetadataQueueFactory, component=factory)
