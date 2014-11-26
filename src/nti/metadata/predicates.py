#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import zope.intid

from zope import component
from zope import interface

from ZODB.interfaces import IBroken
from ZODB.POSException import POSError

from nti.chatserver.interfaces import IUserTranscriptStorage

from nti.dataserver.interfaces import IUser
from nti.dataserver.interfaces import IPrincipalMetadataObjectsIntIds

def user_messageinfo_iter_intids(user, intids=None, broken=None):
	intids = component.getUtility(zope.intid.IIntIds) if intids is None else intids
	storage = IUserTranscriptStorage(user)
	broken = list() if broken is None else broken
	for transcript in storage.transcripts:
		for message in transcript.Messages:
			try:
				if IBroken.providedBy(message):
					broken.append(message)
					logger.warn("ignoring broken object %s", type(message))
				else:
					uid = intids.queryId(message)
					if uid is None:
						logger.warn("ignoring unregistered object %s", message)
					else:
						yield uid
			except (POSError):
				broken.append(message)
				logger.error("ignoring broken object %s", type(message))

@component.adapter(IUser)
@interface.implementer(IPrincipalMetadataObjectsIntIds)
class _ContainedPrincipalObjectsIntIds(object):

	__slots__ = ()

	def __init__(self, user):
		self.user = user

	def iter_intids(self):
		user = self.user
		for uid in user.iter_intids(only_ntiid_containers=True):
			yield uid

@component.adapter(IUser)
@interface.implementer(IPrincipalMetadataObjectsIntIds)
class _FriendsListsPrincipalObjectsIntIds(object):

	__slots__ = ()

	def __init__(self, user):
		self.user = user

	def iter_intids(self):
		intids = component.getUtility(zope.intid.IIntIds) 
		for obj in self.user.friendsLists.values():
			try:
				if IBroken.providedBy(obj):
					logger.warn("ignoring broken object %s", type(obj))
				else:
					uid = intids.queryId(obj)
					if uid is not None:
						yield uid
			except (POSError):
				logger.error("ignoring broken object %s", type(obj))
			
@component.adapter(IUser)
@interface.implementer(IPrincipalMetadataObjectsIntIds)
class _MessageInfoPrincipalObjectsIntIds(object):

	__slots__ = ()

	def __init__(self, user):
		self.user = user

	def iter_intids(self):
		for uid in user_messageinfo_iter_intids(self.user):
			yield uid

@component.adapter(IUser)
@interface.implementer(IPrincipalMetadataObjectsIntIds)
class _MeetingsPrincipalObjectsIntIds(object):

	__slots__ = ()

	def __init__(self, user):
		self.user = user

	def iter_intids(self):
		storage = IUserTranscriptStorage(self.user)
		intids = component.getUtility(zope.intid.IIntIds) 
		for meeting in storage.meetings:
			try:
				if IBroken.providedBy(meeting):
					logger.warn("ignoring broken object %s", type(meeting))
				else:
					uid = intids.queryId(meeting)
					if uid is None:
						logger.warn("ignoring unregistered object %s", meeting)
					else:
						yield uid
			except (POSError):
				logger.error("ignoring broken object %s", type(meeting))
