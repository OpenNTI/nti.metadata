#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import is_
from hamcrest import none
from hamcrest import is_not
from hamcrest import raises
from hamcrest import calling
from hamcrest import assert_that

from zope import component

from nti.metadata import QUEUE_NAMES

from nti.metadata.interfaces import IMetadataQueueFactory

import nti.testing.base


ZCML_STRING = u"""
<configure  xmlns="http://namespaces.zope.org/zope"
            xmlns:zcml="http://namespaces.zope.org/zcml"
            xmlns:metadata="http://nextthought.com/metadata"
            i18n_domain='nti.dataserver'>

    <include package="zope.component" />

    <include package="." file="meta.zcml" />
    <metadata:registerProcessingQueue />

</configure>
"""


class TestZcml(nti.testing.base.ConfiguringTestBase):

    def test_registration(self):
        self.configure_string(ZCML_STRING)
        factory = component.queryUtility(IMetadataQueueFactory)
        assert_that(factory, is_not(none()))

        assert_that(factory.get_queue(QUEUE_NAMES[0]),
                    is_not(none()))

        assert_that(calling(factory.get_queue).with_args('xxx'),
                    raises(ValueError))

        assert_that(factory._redis(), is_(none()))
