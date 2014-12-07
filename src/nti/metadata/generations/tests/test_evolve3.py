#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import has_key
from hamcrest import has_length
from hamcrest import assert_that

import unittest

from zope import component

from zope.catalog.interfaces import ICatalog

from nti.dataserver.users import User
from nti.dataserver.contenttypes import Note
from nti.dataserver.metadata_index import CATALOG_NAME
from nti.dataserver.metadata_index import IX_REVSHAREDWITH

from nti.metadata.generations import evolve3

from nti.dataserver.tests import mock_dataserver

from nti.metadata.tests import SharedConfiguringTestLayer

from nti.dataserver.tests.mock_dataserver import WithMockDSTrans

class TestEvolve3(unittest.TestCase):

	layer = SharedConfiguringTestLayer

	def _create_user(self, username='nt@nti.com', password='temp001'):
		ds = mock_dataserver.current_mock_ds
		usr = User.create_user(ds, username=username, password=password)
		return usr

	@WithMockDSTrans
	def test_evolve3(self):
		with mock_dataserver.mock_db_trans(self.ds) as connection:
			user_1 = self._create_user('nt1@nti.com')
			user_2 = self._create_user('nt2@nti.com')
			
			note = Note()
			note.body = [unicode('foo')]
			note.creator = 'nt1@nti.com'
			note.containerId = 'foo'
			connection.add(note)
			
			note.addSharingTarget(user_2)
			note = user_1.addContainedObject(note)
			
		with mock_dataserver.mock_db_trans(self.ds) as conn:
			class _context(object): pass
			context = _context()
			context.connection = conn

			total = evolve3.do_evolve(context)
			assert_that(total, is_(1))

		with mock_dataserver.mock_db_trans(self.ds) as conn:
			catalog = component.getUtility(ICatalog, name=CATALOG_NAME)
			assert_that(catalog, has_key(IX_REVSHAREDWITH))
			
			index = catalog[IX_REVSHAREDWITH]
			assert_that(list(index.ids()), has_length(1))
