#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import none
from hamcrest import is_not
from hamcrest import raises
from hamcrest import calling
from hamcrest import assert_that

import unittest

import fudge

from zope import component

from zope.component.hooks import getSite

from nti.coremetadata.interfaces import IDataserver

from nti.metadata.processing import get_job_site

from nti.metadata.tests import SharedConfiguringTestLayer


class TestProcesing(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    @fudge.patch('nti.metadata.processing.get_site_for_site_names')
    def test_get_job_site(self, mock_gs):
        assert_that(get_job_site('xxx'), is_(none()))

        class MockDataserver(object):
            root_folder = {'dataserver2': getSite()}

        mock_ds = MockDataserver()
        component.provideUtility(mock_ds, IDataserver)

        mock_gs.is_callable().returns_fake()
        assert_that(get_job_site('google.com'), is_not(none()))

        mock_gs.is_callable().returns(None)
        assert_that(calling(get_job_site).with_args('unknown.org'),
                    raises(ValueError))

        component.getGlobalSiteManager().unregisterUtility(mock_ds, IDataserver)
