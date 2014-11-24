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

from nti.dataserver.interfaces import IUser
from nti.dataserver.interfaces import IPrincipalMetadataObjectsIntIds

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
