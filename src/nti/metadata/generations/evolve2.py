#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
generation 2.

.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

generation = 2

import zope.intid

from zope import component
from zope.component.hooks import site, setHooks

from nti.dataserver.interfaces import IUser

from nti.metadata import metadata_queue
from nti.metadata.utils import user_messageinfo_iter_intids

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

		queue = metadata_queue()
		if queue is None:
			return total

		users = ds_folder['users']
		for user in users.values():
			if not IUser.providedBy(user):
				continue

			for uid in user_messageinfo_iter_intids(user, intids=intids):
				try:
					queue.add(uid)
					total += 1
				except TypeError:
					# Object already cataloged
					pass

		logger.info('Metadata evolution %s done; %s object(s) put in queue',
					generation, total)
	return total

def evolve(context):
	"""
	Evolve to generation 2 by reindexing the message info objects
	"""
	do_evolve(context)
