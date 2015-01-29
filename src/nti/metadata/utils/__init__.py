#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from ZODB.interfaces import IBroken
from ZODB.POSException import POSError

from nti.chatserver.interfaces import IUserTranscriptStorage

from .. import get_iid

def user_messageinfo_iter_objects(user, broken=None):
	storage = IUserTranscriptStorage(user)
	broken = list() if broken is None else broken
	for transcript in storage.transcripts:
		for message in transcript.Messages:
			try:
				if IBroken.providedBy(message):
					broken.append(message)
					logger.warn("ignoring broken object %s", type(message))
				else:
					yield message
			except (TypeError, POSError):
				broken.append(message)
				logger.error("ignoring broken object %s", type(message))
				
def user_messageinfo_iter_intids(user, intids=None, broken=None):
	broken = list() if broken is None else broken
	for message in user_messageinfo_iter_objects(user, broken=broken):
		try:
			uid = get_iid(message, intids=intids)
			if uid is not None:
				yield uid
		except (TypeError, POSError):
			broken.append(message)
			logger.error("ignoring broken object %s", type(message))
