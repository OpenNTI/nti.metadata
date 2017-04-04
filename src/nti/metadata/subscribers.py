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

from zope.intid.interfaces import IIntIds
from zope.intid.interfaces import IIntIdAddedEvent
from zope.intid.interfaces import IIntIdRemovedEvent

from zope.lifecycleevent.interfaces import IObjectRemovedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

from nti.dataserver.interfaces import IEntity

from nti.metadata import is_indexable
from nti.metadata import metadata_queue
from nti.metadata import dataserver_metadata_catalog

from nti.metadata.utils import delete_entity_metadata
from nti.metadata.utils import clear_replies_to_creator


def query_uid(obj):
    intids = component.queryUtility(IIntIds)
    attribute = getattr(intids, 'attribute', '_ds_intid')
    result = getattr(obj, attribute, None)
    # Fall back to our utility if we need to.
    # Extremely slow if we do __len__
    if result is None and intids is not None:
        result = intids.queryId(obj)
    return result


def add_2_queue(obj):
    iid = query_uid(obj)
    if iid is not None:
        __traceback_info__ = iid
        queue = metadata_queue()
        if queue is not None:
            queue.add(iid)
            return True
    return False


def queue_added(obj):
    if is_indexable(obj):
        try:
            return add_2_queue(obj)
        except TypeError:
            pass
    return False


def queue_modified(obj):
    if is_indexable(obj):
        iid = query_uid(obj)
        if iid is not None:
            __traceback_info__ = iid
            try:
                queue = metadata_queue()
                if queue is not None:
                    queue.update(iid)
                    return True
            except TypeError:
                pass
    return False


def queue_remove(obj):
    if is_indexable(obj):
        iid = query_uid(obj)
        if iid is not None:
            __traceback_info__ = iid
            queue = metadata_queue()
            if queue is not None:
                queue.remove(iid)

# IIntIdRemovedEvent


@component.adapter(interface.Interface, IIntIdRemovedEvent)
def _object_removed(modeled, event):
    queue_remove(modeled)

# IIntIdAddedEvent


@component.adapter(interface.Interface, IIntIdAddedEvent)
def _object_added(modeled, event):
    queue_added(modeled)

# IObjectModifiedEvent


@component.adapter(interface.Interface, IObjectModifiedEvent)
def _object_modified(modeled, event):
    queue_modified(modeled)


@component.adapter(IEntity, IObjectRemovedEvent)
def _on_entity_removed(entity, event):
    username = entity.username
    logger.info("Removing metadata data for user %s", username)
    delete_entity_metadata(dataserver_metadata_catalog(), username)


@component.adapter(IEntity, IObjectRemovedEvent)
def clear_replies_to_creator_when_creator_removed(entity, event):
    clear_replies_to_creator(dataserver_metadata_catalog(), entity.username)
