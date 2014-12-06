#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
generation 3.

.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

generation = 3

import zope.intid

from zope import component
from zope.component.hooks import site, setHooks

from ZODB.POSException import POSError

from nti.dataserver.metadata_index import IX_SHAREDWITH
from nti.dataserver.metadata_index import IX_REVSHAREDWITH
from nti.dataserver.metadata_index import RevSharedWithIndex

from nti.metadata import metadata_catalog

def do_evolve(context):
	setHooks()
	conn = context.connection
	root = conn.root()
	ds_folder = root['nti.dataserver']

	lsm = ds_folder.getSiteManager()
	intids = lsm.getUtility(zope.intid.IIntIds)

	total = 0
	with site(ds_folder):
		assert	component.getSiteManager() == ds_folder.getSiteManager(), \
				"Hooks not installed?"

		catalog = metadata_catalog()
		if catalog is None:
			return None
		
		sharedWithIdx = catalog[IX_SHAREDWITH]
		try:
			index = catalog[IX_REVSHAREDWITH]
		except KeyError:
			index = RevSharedWithIndex(family=intids.family)
			intids.register(index)
			index.__parent__ = catalog
			index.__name__ = IX_REVSHAREDWITH
			catalog[IX_REVSHAREDWITH] = index
		
		for uid in sharedWithIdx.ids():
			try:
				obj = intids.queryObject(uid)
				index.index_doc(uid, obj)
				total += 1
			except POSError:
				logger.error("ignoring broken object %s", uid)
	
		logger.info('Metadata evolution %s done; %s object(s) indexed',
					generation, total)

	return total

def evolve(context):
	"""
	Evolve to generation 3 by adding a revSharedWith index
	"""
	do_evolve(context)
