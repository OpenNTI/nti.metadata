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
from nti.dataserver.interfaces import IMetadataCatalogableObjects

@component.adapter(IUser)
@interface.implementer(IMetadataCatalogableObjects)
class _ContainedPrincipalCatalogableObjects(object):

	__slots__ = ()

	def __init__(self, user):
		self.user = user

	def iter_objects(self):
		return ()
