#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import os
import sys
import time
import signal
import argparse

import zope.exceptions

from zope import component

from ZODB.interfaces import IDatabase

from nti.contentlibrary.interfaces import IContentPackageLibrary

from nti.dataserver.interfaces import IDataserverTransactionRunner

from nti.dataserver.utils import open_all_databases
from nti.dataserver.utils import run_with_dataserver
from nti.dataserver.utils.base_script import set_site
from nti.dataserver.utils.base_script import create_context

from nti.metadata.interfaces import DEFAULT_QUEUE_LIMIT

from nti.metadata.reactor import MIN_INTERVAL
from nti.metadata.reactor import MAX_INTERVAL
from nti.metadata.reactor import DEFAULT_SLEEP
from nti.metadata.reactor import DEFAULT_RETRIES
from nti.metadata.reactor import DEFAULT_INTERVAL
from nti.metadata.reactor import DEFAULT_MAX_BATCH_SIZE

from nti.metadata.reactor import MetadataIndexReactor

def sigint_handler(*args):
	logger.info("Shutting down %s", os.getpid())
	sys.exit(0)

def handler(*args):
	raise SystemExit()

signal.signal(signal.SIGTERM, handler)
signal.signal(signal.SIGINT, sigint_handler)

def main():
	arg_parser = argparse.ArgumentParser(description="Metadata processor")
	arg_parser.add_argument('-v', '--verbose', help="Be verbose", action='store_true',
							 dest='verbose')
	arg_parser.add_argument('--site', dest='site',
							help="Application SITE.")

	arg_parser.add_argument('-r', '--retries',
							 dest='retries',
							 help="Transaction runner retries",
							 type=int,
							 default=DEFAULT_RETRIES)
	arg_parser.add_argument('-s', '--sleep',
							 dest='sleep',
							 help="Transaction runner sleep time (secs)",
							 type=float,
							 default=DEFAULT_SLEEP)

	arg_parser.add_argument('-m', '--mintime',
							 dest='mintime',
							 help="Min poll time interval (secs)",
							 type=int,
							 default=DEFAULT_INTERVAL)
	arg_parser.add_argument('-x', '--maxtime',
							 dest='maxtime',
							 help="Max poll time interval (secs)",
							 type=int,
							 default=DEFAULT_INTERVAL)

	arg_parser.add_argument('-l', '--limit',
							 dest='limit',
							 help="Queue limit",
							 type=int,
							 default=DEFAULT_QUEUE_LIMIT)
	arg_parser.add_argument('-b', '--mbs',
							 dest='max_batch_size',
							 help="Max queue limit",
							 type=int,
							 default=DEFAULT_MAX_BATCH_SIZE)

	arg_parser.add_argument('--pke', help="Don't ignore POSError",
							 action='store_true',
							 dest='allow_pke')

	args = arg_parser.parse_args()
	env_dir = os.getenv('DATASERVER_DIR')
	if not env_dir or not os.path.exists(env_dir) and not os.path.isdir(env_dir):
		raise IOError("Invalid dataserver environment root directory")

	context = create_context(env_dir, with_library=True, plugins=True)
	conf_packages = ('nti.appserver', 'nti.metadata')

	run_with_dataserver(environment_dir=env_dir,
						xmlconfig_packages=conf_packages,
						verbose=args.verbose,
						context=context,
						minimal_ds=True,
						use_transaction_runner=False,
						function=lambda: _process_args(args))

def _load_library():
	library = component.queryUtility(IContentPackageLibrary)
	if library is not None:
		library.syncContentPackages()

def _process_args(args):
	import logging

	mintime = args.mintime
	maxtime = args.maxtime
	assert mintime <= maxtime and mintime > 0

	mintime = max(min(mintime, MAX_INTERVAL), MIN_INTERVAL)
	maxtime = max(min(maxtime, MAX_INTERVAL), MIN_INTERVAL)
	
	limit = args.limit
	assert limit > 0
	
	max_batch_size = args.max_batch_size
	assert max_batch_size > 0 and max_batch_size >= limit

	retries = args.retries
	assert retries >= 1 and retries <= 5

	sleep = args.sleep
	assert sleep >= 0 and sleep <= 10

	ignore_pke = not args.allow_pke

	ei = '%(asctime)s %(levelname)-5.5s [%(name)s][%(thread)d][%(threadName)s] %(message)s'
	logging.root.handlers[0].setFormatter(zope.exceptions.log.Formatter(ei))

	# open connections to all databases
	# so they can be recycled in the connection pool
	db = component.getUtility(IDatabase)
	open_all_databases(db, close_children=False)

	# load all libraries
	transaction_runner = component.getUtility(IDataserverTransactionRunner)
	transaction_runner(_load_library)

	# XXX. set site if available should be set after loading the library
	set_site(args.site)
	
	# create and run reactor
	target = MetadataIndexReactor(min_time=mintime,
								  max_time=maxtime, 
								  limit=limit,
								  max_batch_size=max_batch_size,
						  		  retries=retries, 
						  		  sleep=sleep,
						  		  ignore_pke=ignore_pke)
	result = target(time.sleep)
	sys.exit(result)

if __name__ == '__main__':
	main()
