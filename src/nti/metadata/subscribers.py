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

from nti.coremetadata.interfaces import IUser
from nti.coremetadata.interfaces import IUserLastSeenEvent
from nti.coremetadata.interfaces import IUserProcessedContextsEvent

from nti.metadata import is_indexable
from nti.metadata import queue_metadata_add
from nti.metadata import queue_metadata_removed
from nti.metadata import queue_metadata_modififed
from nti.metadata import queue_user_last_seen_event
from nti.metadata import queue_user_processed_contexts_event

logger = __import__('logging').getLogger(__name__)


LAST_SEEN_UPDATE_BUFFER_IN_SEC = 60


@component.adapter(IIntIdAddedEvent)
def _object_added(event):
    modeled = event.object
    if is_indexable(modeled):
        queue_metadata_add(modeled)


@component.adapter(IIntIdRemovedEvent)
def _object_removed(event):
    modeled = event.object
    if is_indexable(modeled):
        queue_metadata_removed(modeled)


@component.adapter(interface.Interface, IObjectModifiedEvent)
def _object_modified(modeled, unused_event=None):
    if is_indexable(modeled):
        queue_metadata_modififed(modeled)


@component.adapter(IUser, IUserLastSeenEvent)
def _on_user_lastseen(user, event):
    # Only update last seen if we are past our buffer threshold
    if      user.lastSeenTime \
        and user.lastSeenTime + LAST_SEEN_UPDATE_BUFFER_IN_SEC > event.timestamp:
        return
    queue_user_last_seen_event(user, event)


@component.adapter(IUser, IUserProcessedContextsEvent)
def _on_user_processed_contexts(user, event):
    queue_user_processed_contexts_event(user,
                                        event.context_ids,
                                        event.timestamp)
