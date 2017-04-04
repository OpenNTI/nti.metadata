#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope.container.contained import Contained

from zope.deprecation import deprecated

from zc.catalogqueue.CatalogEventQueue import CatalogEventQueue

from zc.catalogqueue.queue import CatalogQueue

deprecated("MetadataEventQueue", "no longer used")
class MetadataEventQueue(CatalogEventQueue, Contained):
    pass


deprecated("MetadataQueue", "no longer used")
class MetadataQueue(CatalogQueue, Contained):
    pass
