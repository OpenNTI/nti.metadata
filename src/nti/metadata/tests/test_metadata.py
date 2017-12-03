#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

import unittest

import fakeredis

import fudge

from zope import component
from zope import lifecycleevent

from zope.event import notify

from zope.intid.interfaces import IIntIds
from zope.intid.interfaces import IntIdAddedEvent
from zope.intid.interfaces import IntIdRemovedEvent

from nti.coremetadata.interfaces import IRedisClient

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
