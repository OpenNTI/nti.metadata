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

from .utils import user_messageinfo_iter_intids

def get_uid(obj, intids=None):
	intids = component.getUtility(zope.intid.IIntIds) if intids is None else intids
	try:
		if IBroken.providedBy(obj):
			logger.warn("ignoring broken object %s", type(obj))
		else:
			uid = intids.queryId(obj)
			if uid is None:
				logger.warn("ignoring unregistered object %s", obj)
			else:
				return uid
	except (POSError):
		logger.error("ignoring broken object %s", type(obj))
	return None

@component.adapter(IUser)
@interface.implementer(IPrincipalMetadataObjectsIntIds)
class _ContainedPrincipalObjectsIntIds(object):

	__slots__ = ('user',)

	def __init__(self, user):
		self.user = user

	def iter_intids(self):
		user = self.user
		for uid in user.iter_intids(only_ntiid_containers=True):
			yield uid

@component.adapter(IUser)
@interface.implementer(IPrincipalMetadataObjectsIntIds)
class _FriendsListsPrincipalObjectsIntIds(object):

	__slots__ = ('user',)

	def __init__(self, user):
		self.user = user

	def iter_intids(self):
		intids = component.getUtility(zope.intid.IIntIds) 
		for obj in self.user.friendsLists.values():
			uid = get_uid(obj, intids=intids)
			if uid is not None:
				yield uid
			
@component.adapter(IUser)
@interface.implementer(IPrincipalMetadataObjectsIntIds)
class _MessageInfoPrincipalObjectsIntIds(object):

	__slots__ = ('user',)

	def __init__(self, user):
		self.user = user

	def iter_intids(self):
		for uid in user_messageinfo_iter_intids(self.user):
			yield uid

@component.adapter(IUser)
@interface.implementer(IPrincipalMetadataObjectsIntIds)
class _MeetingsPrincipalObjectsIntIds(object):

	__slots__ = ('user',)

	def __init__(self, user):
		self.user = user

	def iter_intids(self):
		storage = IUserTranscriptStorage(self.user)
		intids = component.getUtility(zope.intid.IIntIds) 
		for meeting in storage.meetings:
			uid = get_uid(meeting, intids=intids)
			if uid is not None:
				yield uid
