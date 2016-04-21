#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from nti.chatserver.interfaces import IUserTranscriptStorage

from nti.metadata import get_iid

from nti.zodb import isBroken

def user_messageinfo_iter_objects(user, broken=None):
	storage = IUserTranscriptStorage(user)
	for transcript in storage.transcripts:
		for message in transcript.Messages:
			if broken is not None and isBroken(message):
				broken.append(message)
			else:
				yield message

def user_messageinfo_iter_intids(user, intids=None, broken=None):
	for message in user_messageinfo_iter_objects(user, broken=broken):
		uid = get_iid(message, intids=intids)
		if uid is not None:
			yield uid
