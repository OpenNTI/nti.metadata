# -*- coding: utf-8 -*-
"""
schema generation installation.

.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

generation = 2

import zope.intid

from zope import component
from zope.component.hooks import site, setHooks

from zope.generations.generations import SchemaManager

from nti.metadata.queue import MetadataQueue
from nti.metadata.interfaces import IMetadataQueue

class _MetadataSchemaManager(SchemaManager):
	"""
	A schema manager that we can register as a utility in ZCML.
	"""
	def __init__(self):
		super(_MetadataSchemaManager, self).__init__(
											generation=generation,
											minimum_generation=generation,
											package_name='nti.metadata.generations')

def do_evolve(context):
	setHooks()
	conn = context.connection
	root = conn.root()
	ds_folder = root['nti.dataserver']

	lsm = ds_folder.getSiteManager()
	intids = lsm.getUtility(zope.intid.IIntIds)

	with site(ds_folder):
		assert	component.getSiteManager() == ds_folder.getSiteManager(), \
				"Hooks not installed?"

		# Register our queue
		queue = MetadataQueue()
		queue.__parent__ = ds_folder
		queue.__name__ = '++etc++metadata++queue'
		intids.register(queue)
		lsm.registerUtility(queue, provided=IMetadataQueue)

		logger.info( 'nti.metadata install complete.' )
		return

def evolve(context):
	do_evolve(context)
