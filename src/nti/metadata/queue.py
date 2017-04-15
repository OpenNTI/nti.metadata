#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from zope.location.interfaces import IContained

from zope.deprecation import deprecated

from zc.catalogqueue.CatalogEventQueue import CatalogEventQueue

from zc.catalogqueue.queue import CatalogQueue


deprecated("MetadataEventQueue", "no longer used")
@interface.implementer(IContained)
class MetadataEventQueue(CatalogEventQueue):
    __parent__ = __name__ = None


deprecated("MetadataQueue", "no longer used")
@interface.implementer(IContained)
class MetadataQueue(CatalogQueue):
    __parent__ = __name__ = None
