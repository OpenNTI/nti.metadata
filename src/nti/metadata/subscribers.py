#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import component
from zope import interface

from zope.intid.interfaces import IIntIdAddedEvent
from zope.intid.interfaces import IIntIdRemovedEvent

from zope.lifecycleevent.interfaces import IObjectModifiedEvent

from nti.metadata import queue_add
from nti.metadata import is_indexable
from nti.metadata import queue_removed
from nti.metadata import queue_modififed

logger = __import__('logging').getLogger(__name__)


@component.adapter(interface.Interface, IIntIdAddedEvent)
def _object_added(modeled, _):
    if is_indexable(modeled):
        queue_add(modeled)


@component.adapter(interface.Interface, IIntIdRemovedEvent)
def _object_removed(modeled, _):
    if is_indexable(modeled):
        queue_removed(modeled)


@component.adapter(interface.Interface, IObjectModifiedEvent)
def _object_modified(modeled, _):
    if is_indexable(modeled):
        queue_modififed(modeled)
