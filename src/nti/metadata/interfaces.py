#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division

__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from zope.deprecation import deprecated


deprecated('IIndexReactor', 'No longer used')
class IIndexReactor(interface.Interface):
    pass


deprecated('IMetadataEventQueue', 'No longer used')
class IMetadataEventQueue(interface.Interface):
    pass


deprecated('IMetadataQueue', 'No longer used')
class IMetadataQueue(interface.Interface):
    pass


class IMetadataQueueFactory(interface.Interface):
    """
    A factory for metadata queues.
    """

class INoMetadataAutoIndex(interface.Interface):
    """
    Marker for objects that should not be automatically indexed
    """
