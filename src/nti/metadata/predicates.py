#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component
from zope import interface

from nti.chatserver.interfaces import IUserTranscriptStorage

from nti.dataserver.interfaces import IUser
from nti.dataserver.interfaces import IIntIdIterable
from nti.dataserver.interfaces import IPrincipalMetadataObjects

from .utils import user_messageinfo_iter_objects

from . import get_uid

@interface.implementer(IIntIdIterable, IPrincipalMetadataObjects)
class BasePrincipalObjects(object):
	
	def __init__(self, user=None, *args, **kwargs):
		self.user = user
		
	def iter_intids(self, intids=None):
		for obj in self.iter_objects():
			uid = get_uid(obj, intids=intids)
			if uid is not None:
				yield uid 
			
	def iter_objects(self):
		raise NotImplementedError()

@component.adapter(IUser)
class _ContainedPrincipalObjects(BasePrincipalObjects):

	def iter_objects(self):
		user = self.user
		for uid in user.iter_objects(only_ntiid_containers=True):
			yield uid

@component.adapter(IUser)
class _FriendsListsPrincipalObjects(BasePrincipalObjects):

	def iter_objects(self):
		for obj in self.user.friendsLists.values():
			yield obj
			
@component.adapter(IUser)
@interface.implementer(IPrincipalMetadataObjects)
class _MessageInfoPrincipalObjects(BasePrincipalObjects):

	def iter_objects(self):
		for uid in user_messageinfo_iter_objects(self.user):
			yield uid

@component.adapter(IUser)
class _MeetingPrincipalObjects(BasePrincipalObjects):

	def iter_objects(self):
		storage = IUserTranscriptStorage(self.user)
		for meeting in storage.meetings:
			yield meeting
