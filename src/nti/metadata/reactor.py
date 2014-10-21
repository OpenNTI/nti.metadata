#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from nti.monkey import relstorage_patch_all_except_gevent_on_import
relstorage_patch_all_except_gevent_on_import.patch()

import os
import time
import gevent
import random
import functools

from zope import component
from zope import interface
from zope.component import ComponentLookupError

from ZODB import loglevels
from ZODB.POSException import POSKeyError
from ZODB.POSException import ConflictError

from redis.connection import ConnectionError

from nti.dataserver.interfaces import IDataserverTransactionRunner

from nti.zodb.interfaces import UnableToAcquireCommitLock

from nti.metadata import process_queue

from nti.metadata.interfaces import IIndexReactor
from nti.metadata.interfaces import DEFAULT_QUEUE_LIMIT

MIN_INTERVAL = 5
MAX_INTERVAL = 60
MIN_BATCH_SIZE = 10

DEFAULT_SLEEP = 1
DEFAULT_RETRIES = 2
DEFAULT_INTERVAL = 30

POS_KEY_ERROR_RT = -2
CONFLICT_ERROR_RT = -1

def process_index_msgs(limit=DEFAULT_QUEUE_LIMIT,
					   use_trx_runner=True,
					   retries=DEFAULT_RETRIES,
					   sleep=DEFAULT_SLEEP ):

	result = 0
	try:
		runner = functools.partial(process_queue, limit=limit)
		if use_trx_runner:
			trx_runner = component.getUtility(IDataserverTransactionRunner)
			result = trx_runner(runner, retries=retries, sleep=sleep)
		else:
			result = runner()
	except POSKeyError:
		logger.exception("Cannot index object(s)")
		result = POS_KEY_ERROR_RT
	except (UnableToAcquireCommitLock, ConflictError) as e:
		logger.error(e)
		result = CONFLICT_ERROR_RT
	except (TypeError, StandardError): # Cache errors?
		logger.exception('Cannot process index messages')
		raise
	return result

@interface.implementer(IIndexReactor)
class MetadataIndexReactor(object):
	# TODO This alg should be merged into nti.async.

	# transaction runner
	sleep = DEFAULT_SLEEP
	retries = DEFAULT_RETRIES
	# wait time
	min_wait_time = 10
	max_wait_time = 30
	# batch size
	limit = DEFAULT_QUEUE_LIMIT

	stop = False
	start_time = 0
	processor = pid = None

	def __init__(self, min_time=None, max_time=None, limit=None,
				 retries=None, sleep=None):

		if min_time:
			self.min_wait_time = min_time

		if max_time:
			self.max_wait_time = max_time

		if limit and limit != DEFAULT_QUEUE_LIMIT:
			self.limit = limit

		if sleep:
			self.sleep = sleep

		if retries:
			self.retries = retries

	def __repr__(self):
		return "%s" % (self.__class__.__name__.lower())

	def halt(self):
		self.stop = True

	def start(self):
		if self.processor is None:
			self.processor = self._spawn_index_processor()
		return self

	def run(self, sleep=gevent.sleep):
		result = 0
		self.stop = False
		self.pid = os.getpid()
		generator = random.Random()
		self.start_time = time.time()
		try:
			batch_size = self.limit
			logger.info("Metadata index reactor started")
			while not self.stop:
				start = time.time()
				try:
					if not self.stop:
						result = process_index_msgs(limit=batch_size,
												 	sleep=self.sleep,
												 	retries=self.retries )
						duration = time.time() - start
						if result == 0: # no work
							batch_size = self.limit  # reset to default
							secs = generator.randint(self.min_wait_time,
													 self.max_wait_time)
							duration = secs
						elif result < 0:  # conflict error/exception
							factor = 0.33 if result == CONFLICT_ERROR_RT else 0.2
							batch_size = max(MIN_BATCH_SIZE, int(batch_size * factor))
							duration = min(duration * 2.0, MAX_INTERVAL * 3.0)
						elif duration < MAX_INTERVAL:
							batch_size = int(batch_size * 1.5)
							half = int(duration / 2.0)
							secs = generator.randint(self.min_wait_time,
												  	 max(self.min_wait_time, half))
							duration = secs
						else:
							half = batch_size * .5
							batch_size = max(MIN_BATCH_SIZE, int(half / duration))
							secs = generator.randint(self.min_wait_time,
													 self.max_wait_time)
							duration = secs

						logger.log(loglevels.TRACE, "Sleeping %s(secs). Batch size %s",
								   duration, batch_size)
						sleep(duration)
				except ComponentLookupError:
					result = 99
					logger.error("process could not get component", self.pid)
					break
				except KeyboardInterrupt:
					break
				except ConnectionError:
					result = 66
					logger.exception("%s could not connect to redis", self.pid)
					break
				except (TypeError, StandardError):
					result = 77 # Cache errors?
					break
				except:
					logger.exception("Unhandled exception")
					raise
		finally:
			self.processor = None
		return result

	__call__ = run

	def _spawn_index_processor(self):
		result = gevent.spawn(self.run)
		return result
