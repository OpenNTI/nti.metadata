#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import has_length
from hamcrest import assert_that

import unittest

import zc.intid as zc_intid

from zope import component

from zope.catalog.interfaces import ICatalog

from nti.chatserver.meeting import _Meeting as Meet
from nti.chatserver.messageinfo import MessageInfo as Msg
from nti.chatserver.interfaces import IUserTranscriptStorage

from nti.dataserver.users import User
from nti.dataserver.metadata_index import CATALOG_NAME

from nti.metadata.generations import evolve2

from nti.dataserver.tests import mock_dataserver

from nti.metadata.tests import SharedConfiguringTestLayer

from nti.dataserver.tests.mock_dataserver import WithMockDSTrans

class TestEvolve2(unittest.TestCase):

	layer = SharedConfiguringTestLayer

	def _create_user(self, username='nt@nti.com', password='temp001'):
		ds = mock_dataserver.current_mock_ds
		usr = User.create_user(ds, username=username, password=password)
		return usr

	@WithMockDSTrans
	def test_evolve2(self):
		with mock_dataserver.mock_db_trans(self.ds) as conn:
			user = self._create_user()
			storage = IUserTranscriptStorage(user)
			msg = Msg()
			meet = Meet()
			meet.containerId = u'tag:nti:foo'
			meet.creator = user
			meet.ID = 'the_meeting'
			msg.containerId = meet.containerId
			msg.ID = '42'
			msg.creator = user
			msg.__parent__ = meet
			
			conn.add( msg )
			conn.add( meet )
			component.getUtility( zc_intid.IIntIds ).register( msg )
			component.getUtility( zc_intid.IIntIds ).register( meet )
			storage.add_message( meet, msg )

		with mock_dataserver.mock_db_trans(self.ds) as conn:
			class _context(object): pass
			context = _context()
			context.connection = conn
	
			total = evolve2.do_evolve(context)
			assert_that(total, is_(1))
				
		with mock_dataserver.mock_db_trans(self.ds) as conn:
			catalog = component.getUtility(ICatalog, name=CATALOG_NAME)
			
			# Everything is in the catalog as it should be
			for query in ( {'containerId': {'any_of': ('tag:nti:foo',) }},
						   {'creator': {'any_of': ('nt@nti.com',)} },
						   {'mimeType': {'any_of': ('application/vnd.nextthought.messageinfo',)}} ):
				results = list(catalog.searchResults(**query))
				assert_that( results, has_length(1))
		