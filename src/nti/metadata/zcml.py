#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
Directives to be used in ZCML

.. $Id$
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

	def add( self, val ):
		# Process immediately
		queue = component.queryUtility(IMetadataQueue)
		if queue is not None:
			queue.add( val )
			process_queue( queue=queue )

	def update(self, val):
		queue = component.queryUtility(IMetadataQueue)
		if queue is not None:
			queue.update( val )
			process_queue( queue=queue )

	def remove(self, val):
		queue = component.queryUtility(IMetadataQueue)
		if queue is not None:
			queue.remove( val )
			process_queue( queue=queue )

@interface.implementer(IMetadataQueueFactory)
class _ImmediateQueueFactory(object):

	__slots__ = ()
	
	def get_queue( self ):
		return ImmediateQueueRunner()

@interface.implementer(IMetadataQueueFactory)
class _ProcessingQueueFactory(object):

	__slots__ = ()
	
	def get_queue( self ):
		queue = component.queryUtility(IMetadataQueue)
		return queue

def registerImmediateProcessingQueue(_context):
	logger.info( "Registering immediate processing queue" )
	factory = _ImmediateQueueFactory()
	utility( _context, provides=IMetadataQueueFactory, component=factory)

def registerProcessingQueue(_context):
	logger.info( "Registering processing queue" )
	factory = _ProcessingQueueFactory()
	utility( _context, provides=IMetadataQueueFactory, component=factory)
