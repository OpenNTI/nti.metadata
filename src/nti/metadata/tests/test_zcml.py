#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import none
from hamcrest import is_not
from hamcrest import assert_that

from zope import component

from nti.metadata.interfaces import IMetadataQueueFactory

import nti.testing.base

ZCML_STRING = """
<configure  xmlns="http://namespaces.zope.org/zope"
            xmlns:zcml="http://namespaces.zope.org/zcml"
            xmlns:metadata="http://nextthought.com/metadata"
            i18n_domain='nti.dataserver'>

    <include package="zope.component" />
    <include package="zope.annotation" />
    <include package="z3c.baseregistry" file="meta.zcml" />

    <include package="." file="meta.zcml" />
    <metadata:registerProcessingQueue />

</configure>
"""


class TestZcml(nti.testing.base.ConfiguringTestBase):

    def test_registration(self):
        self.configure_string(ZCML_STRING)

        factory = component.queryUtility(IMetadataQueueFactory)
        assert_that(factory, is_not(none()))
