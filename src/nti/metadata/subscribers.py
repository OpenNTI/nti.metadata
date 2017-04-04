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

from zope.intid.interfaces import IIntIdAddedEvent
from zope.intid.interfaces import IIntIdRemovedEvent

from zope.lifecycleevent.interfaces import IObjectRemovedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

from nti.dataserver.interfaces import IEntity

from nti.metadata import queue_add
from nti.metadata import is_indexable
from nti.metadata import queue_removed
from nti.metadata import queue_modififed
from nti.metadata import dataserver_metadata_catalog

from nti.metadata.utils import delete_entity_metadata
from nti.metadata.utils import clear_replies_to_creator


@component.adapter(interface.Interface, IIntIdAddedEvent)
def _object_added(modeled, event):
    if is_indexable(modeled):
        queue_add(modeled)


@component.adapter(interface.Interface, IIntIdRemovedEvent)
def _object_removed(modeled, event):
    if is_indexable(modeled):
        queue_removed(modeled)


@component.adapter(interface.Interface, IObjectModifiedEvent)
def _object_modified(modeled, event):
    if is_indexable(modeled):
        queue_modififed(modeled)


@component.adapter(IEntity, IObjectRemovedEvent)
def _on_entity_removed(entity, event):
    username = entity.username
    logger.info("Removing metadata data for user %s", username)
    delete_entity_metadata(dataserver_metadata_catalog(), username)


@component.adapter(IEntity, IObjectRemovedEvent)
def clear_replies_to_creator_when_creator_removed(entity, event):
    clear_replies_to_creator(dataserver_metadata_catalog(), entity.username)
