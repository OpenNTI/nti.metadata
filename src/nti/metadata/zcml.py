#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import component
from zope import interface

from zope.component.zcml import utility

from nti.asynchronous import get_job_queue as async_queue

from nti.asynchronous.interfaces import IRedisQueue

from nti.asynchronous.redis_queue import RedisQueue

from nti.coremetadata.interfaces import IRedisClient

from nti.metadata import QUEUE_NAMES

from nti.metadata.interfaces import IMetadataQueueFactory

logger = __import__('logging').getLogger(__name__)


class ImmediateQueueRunner(object):
    """
    A queue that immediately runs the given job. This is generally
    desired for test or dev mode.
    """

    def put(self, job):
        job()


@interface.implementer(IMetadataQueueFactory)
class _ImmediateQueueFactory(object):

    def get_queue(self, _):
        return ImmediateQueueRunner()


@interface.implementer(IMetadataQueueFactory)
class _AbstractProcessingQueueFactory(object):

    queue_interface = None

    def get_queue(self, name):
        queue = async_queue(name, self.queue_interface)
        if queue is None:
            raise ValueError("No queue exists for metadata queue (%s)." % name)
        return queue


class _MetadataQueueFactory(_AbstractProcessingQueueFactory):

    queue_interface = IRedisQueue

    def __init__(self, _context):
        for name in QUEUE_NAMES:
            queue = RedisQueue(self._redis, name)
            utility(_context, provides=IRedisQueue, component=queue, name=name)

    def _redis(self):
        return component.getUtility(IRedisClient)


def registerImmediateProcessingQueue(_context):
    logger.info("Registering immediate metadata queue")
    factory = _ImmediateQueueFactory()
    utility(_context, provides=IMetadataQueueFactory, component=factory)


def registerProcessingQueue(_context):
    logger.info("Registering metadata redis queue")
    factory = _MetadataQueueFactory(_context)
    utility(_context, provides=IMetadataQueueFactory, component=factory)
