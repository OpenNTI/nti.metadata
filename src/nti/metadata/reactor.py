#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import os
import time
import gevent
import random
from functools import partial

from zope import component
from zope import interface

from zope.component import ComponentLookupError

from ZODB.POSException import POSError
from ZODB.POSException import ConflictError

from nti.dataserver.interfaces import IDataserverTransactionRunner

from nti.metadata import process_queue

from nti.metadata.interfaces import IIndexReactor
from nti.metadata.interfaces import DEFAULT_QUEUE_LIMIT

from nti.transactions import DEFAULT_LONG_RUNNING_COMMIT_IN_SECS

from nti.zodb.interfaces import UnableToAcquireCommitLock

#: Min interval time in sec
MIN_INTERVAL = 5

#: Max interval time in sec
MAX_INTERVAL = 60

#: Default time interval
DEFAULT_INTERVAL = 15

#: Min batch size
MIN_BATCH_SIZE = 10

#: Default max batch size
DEFAULT_MAX_BATCH_SIZE = 2500

#: Default sleep times
DEFAULT_SLEEP = 1

#: Default number of retries
DEFAULT_RETRIES = 2

#: ZODB POSErorr code
POS_ERROR_RT = -2

#: ZODB conflict error
CONFLICT_ERROR_RT = -1

def process_index_msgs(ignore_pke=True,
					   use_trx_runner=True,
					   sleep=DEFAULT_SLEEP,
					   retries=DEFAULT_RETRIES,
					   limit=DEFAULT_QUEUE_LIMIT):

	result = 0
	try:
		runner = partial(process_queue, limit=limit, ignore_pke=ignore_pke)
		if use_trx_runner:
			trx_runner = component.getUtility(IDataserverTransactionRunner)
			result = trx_runner(runner, retries=retries, sleep=sleep)
		else:
			result = runner()
	except POSError:
		logger.exception("Cannot index object(s)")
		result = POS_ERROR_RT
	except (UnableToAcquireCommitLock, ConflictError) as e:
		logger.error(e)
		result = CONFLICT_ERROR_RT
	except (TypeError, StandardError):  # Cache errors?
		logger.exception('Cannot process index messages')
		raise
	return result

@interface.implementer(IIndexReactor)
class MetadataIndexReactor(object):

	stop = False
	start_time = 0
	processor = pid = None

	def __init__(self, 
				 # wait time
				 min_time=None, 
				 max_time=None, 
				 # batch size
				 limit=None,
				 max_batch_size=None,
				 # transaction params
				 retries=None, 
				 sleep=None, 
				 # ignore POSErrors
				 ignore_pke=True):

		self.sleep = sleep or DEFAULT_SLEEP
		self.retries = retries or DEFAULT_RETRIES

		self.limit = limit or DEFAULT_QUEUE_LIMIT
		self.max_batch_size = max_batch_size or DEFAULT_MAX_BATCH_SIZE
		
		self.min_wait_time = min_time or MIN_INTERVAL
		self.max_wait_time = max_time or MAX_INTERVAL

		self.ignore_pke = True if ignore_pke is None else ignore_pke

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
												 	retries=self.retries,
												 	ignore_pke=self.ignore_pke)
						duration = time.time() - start
						if result == 0:  # no work
							batch_size = self.limit  # reset to default
							duration = generator.randint(self.min_wait_time,
														 self.max_wait_time)
						elif result < 0:  # conflict error/exception
							factor = 0.33 if result == CONFLICT_ERROR_RT else 0.2
							batch_size = max(MIN_BATCH_SIZE, int(batch_size * factor))
							duration = min(duration * 2.0, MAX_INTERVAL * 3.0)
						elif duration > DEFAULT_LONG_RUNNING_COMMIT_IN_SECS:
							batch_size = max(MIN_BATCH_SIZE, int(batch_size * 0.5))
							duration = generator.randint(self.min_wait_time,
													 	 self.max_wait_time)
						elif duration < MAX_INTERVAL:
							batch_size = int(batch_size * 1.5)
							half = int(duration / 2.0)
							duration = generator.randint(self.min_wait_time,
												  	 	 max(self.min_wait_time, half))
						else:
							half = batch_size * .5
							batch_size = max(MIN_BATCH_SIZE, int(half / duration))
							duration = generator.randint(self.min_wait_time,
													 	 self.max_wait_time)

						batch_size = min(batch_size, self.max_batch_size)
						if batch_size == self.max_batch_size:
							duration = min(duration, MIN_INTERVAL)

						sleep(duration)
				except ComponentLookupError:
					result = 99
					logger.error("process could not get component", self.pid)
					break
				except KeyboardInterrupt:
					break
				except (TypeError, StandardError):
					result = 77  # Cache errors?
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
