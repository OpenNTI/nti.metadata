# -*- coding: utf-8 -*-
"""
schema generation installation.

.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

generation = 5

from zope import component

from zope.component.hooks import site
from zope.component.hooks import setHooks

from zope.generations.generations import SchemaManager

from zope.intid.interfaces import IIntIds

from nti.metadata.interfaces import IMetadataQueue

from nti.metadata.queue import MetadataQueue

class _MetadataSchemaManager(SchemaManager):
	"""
	A schema manager that we can register as a utility in ZCML.
	"""
	def __init__(self):
		super(_MetadataSchemaManager, self).__init__(
											generation=generation,
											minimum_generation=generation,
											package_name='nti.metadata.generations')

def install_metadata_queue(ds_folder):
	lsm = ds_folder.getSiteManager()
	intids = lsm.getUtility(IIntIds)

	# Register our queue
	queue = MetadataQueue()
	queue.__parent__ = ds_folder
	queue.__name__ = '++etc++metadata++queue'
	intids.register(queue)
	lsm.registerUtility(queue, provided=IMetadataQueue)
		
def do_evolve(context):
	setHooks()
	conn = context.connection
	root = conn.root()
	ds_folder = root['nti.dataserver']

	with site(ds_folder):
		assert	component.getSiteManager() == ds_folder.getSiteManager(), \
				"Hooks not installed?"

		install_metadata_queue(ds_folder)
		logger.info('nti.metadata install complete.')
		return

def evolve(context):
	do_evolve(context)
