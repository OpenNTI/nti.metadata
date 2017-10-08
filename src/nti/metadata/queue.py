#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import interface

from zope.location.interfaces import IContained

from zope.deprecation import deprecated

from persistent import Persistent

logger = __import__('logging').getLogger(__name__)


deprecated("MetadataEventQueue", "no longer used")
@interface.implementer(IContained)
class MetadataEventQueue(Persistent):
    __parent__ = __name__ = None


deprecated("MetadataQueue", "no longer used")
@interface.implementer(IContained)
class MetadataQueue(Persistent):
    __parent__ = __name__ = None
