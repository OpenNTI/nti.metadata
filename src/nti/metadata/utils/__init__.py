#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import zope.intid

from zope import component

from ZODB.interfaces import IBroken
from ZODB.POSException import POSError

from nti.chatserver.interfaces import IUserTranscriptStorage

def user_messageinfo_iter_intids(user, intids=None, broken=None):
    intids = component.getUtility(zope.intid.IIntIds) if intids is None else intids
    storage = IUserTranscriptStorage(user)
    broken = list() if broken is None else broken
    for transcript in storage.transcripts:
        for message in transcript.Messages:
            try:
                if IBroken.providedBy(message):
                    broken.append(message)
                    logger.warn("ignoring broken object %s", type(message))
                else:
                    uid = intids.queryId(message)
                    if uid is None:
                        logger.warn("ignoring unregistered object %s", message)
                    else:
                        yield uid
            except (TypeError, POSError):
                broken.append(message)
                logger.error("ignoring broken object %s", type(message))