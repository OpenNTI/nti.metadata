#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

generation = 5

from zope import component
from zope import interface

from zope.component.hooks import setHooks
from zope.component.hooks import site as current_site

from zope.intid.interfaces import IIntIds

from nti.zope_catalog.interfaces import IMetadataCatalog

from nti.dataserver.interfaces import IDataserver
from nti.dataserver.interfaces import IOIDResolver

from nti.dataserver.metadata_index import IX_TOPICS
from nti.dataserver.metadata_index import IX_MIMETYPE
from nti.dataserver.metadata_index import CATALOG_NAME
from nti.dataserver.metadata_index import TP_USER_GENERATED_DATA
from nti.dataserver.metadata_index import IsUserGeneratedDataExtentFilteredSet

from nti.metadata import metadata_queue

@interface.implementer(IDataserver)
class MockDataserver(object):

	root = None

	def get_by_oid(self, oid, ignore_creator=False):
		resolver = component.queryUtility(IOIDResolver)
		if resolver is None:
			logger.warn("Using dataserver without a proper ISiteManager configuration.")
		else:
			return resolver.get_object_by_oid(oid, ignore_creator=ignore_creator)
		return None

def do_evolve(context, generation=generation):
	setHooks()
	conn = context.connection
	ds_folder = conn.root()['nti.dataserver']

	mock_ds = MockDataserver()
	mock_ds.root = ds_folder
	component.provideUtility(mock_ds, IDataserver)

	lsm = ds_folder.getSiteManager()
	intids = lsm.getUtility(IIntIds)
	with current_site(ds_folder):
		assert	component.getSiteManager() == ds_folder.getSiteManager(), \
				"Hooks not installed?"

		catalog = lsm.getUtility(provided=IMetadataCatalog, name=CATALOG_NAME)

		topics = catalog[IX_TOPICS]
		if TP_USER_GENERATED_DATA not in topics._filters:
			the_filter = IsUserGeneratedDataExtentFilteredSet(TP_USER_GENERATED_DATA, 
															  family=intids.family)
			topics.addFilter(the_filter)
	
			queue = metadata_queue()
			if queue is not None:
				mimeTypeIdx = catalog[IX_MIMETYPE]
				queue.extend(mimeTypeIdx.ids())

		logger.info('Metadata evolution %s done', generation)

	component.getGlobalSiteManager().unregisterUtility(mock_ds, IDataserver)

def evolve(context):
	"""
	Evolve to generation 5 by adding a IsUserGeneratedDataExtentFilteredSet index
	"""
	do_evolve(context, generation)
