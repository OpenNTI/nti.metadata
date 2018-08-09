#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import is_
from hamcrest import raises
from hamcrest import calling
from hamcrest import assert_that

import unittest

import fakeredis

import fudge

from ZODB.interfaces import IBroken

from zope import component
from zope import interface
from zope import lifecycleevent

from zope.event import notify

from zope.intid.interfaces import IIntIds
from zope.intid.interfaces import IntIdAddedEvent
from zope.intid.interfaces import IntIdRemovedEvent

from nti.coremetadata.interfaces import IRedisClient

from nti.metadata import ADDED
from nti.metadata import queue_event
from nti.metadata import process_event

from nti.metadata.tests import SharedConfiguringTestLayer

from nti.zope_catalog.interfaces import IDeferredCatalog

from nti.zope_catalog.catalog import DeferredCatalog


class TestMetdata(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    def test_events(self):
        fake_obj = fudge.Fake()
        catalog = DeferredCatalog()
        redis = fakeredis.FakeStrictRedis(db=102)

        gsm = component.getGlobalSiteManager()
        gsm.registerUtility(redis, IRedisClient)
        gsm.registerUtility(catalog, IDeferredCatalog)

        class LegacyCatalog(DeferredCatalog):
            def force_index_doc(self, *args):
                pass
        legacy = LegacyCatalog()
        gsm.registerUtility(legacy, IDeferredCatalog, 'legacy')

        class MockIntId(object):

            def queryId(self, unused_obj):
                return 1
            getId = queryId

            def queryObject(self, unused_doc_id):
                return fake_obj
            getObject = queryObject

        intid = MockIntId()
        gsm.registerUtility(intid, IIntIds)

        notify(IntIdAddedEvent(fake_obj, None, intid))

        lifecycleevent.modified(fake_obj)

        notify(IntIdRemovedEvent(fake_obj, None))

        gsm.unregisterUtility(intid, IIntIds)
        gsm.unregisterUtility(redis, IRedisClient)
        gsm.unregisterUtility(catalog, IDeferredCatalog)
        gsm.unregisterUtility(legacy, IDeferredCatalog, 'legacy')

    def test_process_event(self):
        catalog = DeferredCatalog()
        gsm = component.getGlobalSiteManager()
        gsm.registerUtility(catalog, IDeferredCatalog)

        broken = fudge.Fake()
        interface.alsoProvides(broken, IBroken)

        class MockIntId(object):
            def queryObject(self, doc_id):
                if doc_id == 1:
                    return None
                elif doc_id == 2:
                    return broken
                elif doc_id == 3:
                    raise TypeError()

        intid = MockIntId()
        gsm.registerUtility(intid, IIntIds)

        assert_that(process_event(1, ADDED), is_(False))
        assert_that(process_event(2, ADDED), is_(False))
        assert_that(process_event(3, ADDED), is_(False))

        assert_that(calling(process_event).with_args(3, ADDED, False),
                    raises(TypeError))

        gsm.unregisterUtility(intid, IIntIds)
        gsm.unregisterUtility(catalog, IDeferredCatalog)

    @fudge.patch('nti.metadata.add_metadata_to_queue')
    def test_queue_event(self, mock_aq):
        assert_that(queue_event(None, ADDED), is_(False))

        redis = fakeredis.FakeStrictRedis(db=102)
        gsm = component.getGlobalSiteManager()
        gsm.registerUtility(redis, IRedisClient)

        mock_aq.is_callable().returns_fake()

        assert_that(queue_event(1, ADDED), is_(True))
        assert_that(queue_event(fudge.Fake(), ADDED), is_(False))

        gsm.unregisterUtility(redis, IRedisClient)
