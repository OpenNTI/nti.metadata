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

from nti.asynchronous.scheduled import ImmediateQueueRunner as AsyncQueueRunner
from nti.asynchronous.scheduled import NonRaisingImmediateQueueRunner as AsyncNonRaisingQueueRunner

from nti.coremetadata.interfaces import IRedisClient

from nti.metadata import QUEUE_NAMES

from nti.metadata.interfaces import IMetadataQueueFactory

logger = __import__('logging').getLogger(__name__)


class ImmediateQueueRunner(AsyncQueueRunner):
    """
    A queue that immediately runs the given job. This is generally
    desired for test or dev mode.
    """

    def __contains__(self, unused_key):
        return False


class NonRaisingImmediateQueueRunner(AsyncNonRaisingQueueRunner):
    """
    A queue that immediately runs the given job. This is generally
    desired for test or dev mode.
    """

    def __contains__(self, unused_key):
        return False


@interface.implementer(IMetadataQueueFactory)
class _TestImmediateQueueFactory(object):
    """
    Used for inlining jobs during tests. These tests may fail for various
    test ad-hoc reasons. This job runner will swallow such exceptions.

    This should not be used in any live environment.
    """

    def get_queue(self, name):
        return NonRaisingImmediateQueueRunner()


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
        return component.queryUtility(IRedisClient)


def registerImmediateProcessingQueue(_context):
    logger.info("Registering immediate metadata queue")
    factory = _ImmediateQueueFactory()
    utility(_context, provides=IMetadataQueueFactory, component=factory)


def registerTestImmediateProcessingQueue(_context):
    logger.info("Registering test immediate metadata queue")
    factory = _TestImmediateQueueFactory()
    utility(_context, provides=IMetadataQueueFactory, component=factory)


def registerProcessingQueue(_context):
    logger.info("Registering metadata redis queue")
    factory = _MetadataQueueFactory(_context)
    utility(_context, provides=IMetadataQueueFactory, component=factory)
