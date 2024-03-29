#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import component

from zope.component.hooks import getSite
from zope.component.hooks import site as current_site

from nti.asynchronous import create_job

from nti.coremetadata.interfaces import IDataserver

from nti.metadata.interfaces import IMetadataQueueFactory

from nti.site.site import get_site_for_site_names

from nti.site.transient import TrivialSite

logger = __import__('logging').getLogger(__name__)


def job_in_queue(jid, queue, safe=True):
    try:
        result = jid in queue
    except Exception, e: # pylint: disable=broad-except
        if safe:
            result = False
        else:
            raise e
    return result


def queue_factory():
    factory = component.getUtility(IMetadataQueueFactory)
    return factory


def get_site(site_name=None):
    if site_name is None:
        site = getSite()
        site_name = site.__name__ if site is not None else None
    return site_name


def get_job_queue(name):
    factory = queue_factory()
    return factory.get_queue(name)


def get_job_site(job_site_name=None):
    old_site = getSite()
    if job_site_name is None:
        job_site = old_site
    else:
        dataserver = component.queryUtility(IDataserver)
        if dataserver is None:
            return None
        try:
            ds_folder = dataserver.root_folder['dataserver2']
        except KeyError:
            return None
        with current_site(ds_folder):
            job_site = get_site_for_site_names((job_site_name,))
        if job_site is None or isinstance(job_site, TrivialSite):
            raise ValueError('No site found for (%s)' % job_site_name)
    return job_site


def execute_job(*args, **kwargs):
    """
    Performs the actual execution of a job.  We'll attempt to do
    so in the site the event occurred in, otherwise, we'll run in
    whatever site we are currently in.
    """
    event_site_name = kwargs.pop('site_name', None)
    event_site = get_job_site(event_site_name) or getSite()
    with current_site(event_site):
        func, args = args[0], args[1:]
        return func(*args, **kwargs)


def execute_metadata_job(*args, **kwargs):
    return execute_job(*args, **kwargs)


def put_metadata_job(queue_name, func, job_id, site_name=None, **kwargs):
    site_name = get_site(site_name)
    queue = get_job_queue(queue_name)
    job = create_job(execute_metadata_job,
                     func,
                     site_name=site_name,
                     **kwargs)
    job.id = job_id
    queue.put(job)
    return job


def add_metadata_to_queue(queue_name, func, doc_id, event, site_name=None, **kwargs):
    job_id = "%s_%s" % (doc_id, event)
    return put_metadata_job(queue_name,
                            func,
                            event=event,
                            job_id=job_id,
                            doc_id=doc_id,
                            site_name=site_name,
                            **kwargs)
add_to_queue = add_metadata_to_queue  # BWC


def add_user_lastseen_event_to_queue(queue_name, func, doc_id, site_name=None, **kwargs):
    job_id = "%s_user_seen" % doc_id
    return put_metadata_job(queue_name,
                            func,
                            job_id=job_id,
                            doc_id=doc_id,
                            site_name=site_name,
                            **kwargs)

