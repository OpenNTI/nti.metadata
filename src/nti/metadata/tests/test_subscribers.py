#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import none
from hamcrest import is_not
from hamcrest import has_length
from hamcrest import assert_that

import unittest

from nti.contentfragments.interfaces import IPlainTextContentFragment

from nti.dataserver.contenttypes import Note

from nti.dataserver.metadata_index import IX_CREATOR

from nti.dataserver.users import User

from nti.ntiids.ntiids import make_ntiid

from nti.metadata import dataserver_metadata_catalog

from nti.metadata.subscribers import delete_entity_data

from nti.dataserver.tests import mock_dataserver

from nti.dataserver.tests.mock_dataserver import WithMockDSTrans

from nti.metadata.tests import SharedConfiguringTestLayer


class TestSubscribers(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    def _create_user(self, username='nt@nti.com', password='temp001'):
        ds = mock_dataserver.current_mock_ds
        usr = User.create_user(ds, username=username, password=password)
        return usr

    def _create_note(self, msg, owner,title=None, inReplyTo=None):
        note = Note()
        note.body = [msg]
        note.creator = owner
        note.inReplyTo = inReplyTo
        note.title = IPlainTextContentFragment(title) if title else None
        note.containerId = make_ntiid(nttype='bleach', specific='manga')
        return note

    @WithMockDSTrans
    def test_create_delete_notes(self):
        notes = 30
        username = 'ichigo@bleach.org'
        user = self._create_user(username=username)
        connection = mock_dataserver.current_transaction
        for x in range(notes):
            title = u"title %s" % x
            message = u"body %s" % x
            note = self._create_note(message, user, title=title)
            connection.add(note)
            user.addContainedObject(note)

        catalog = dataserver_metadata_catalog()
        assert_that(catalog, is_not(none()))
        query = {IX_CREATOR: {'any_of': (username,)}}
        results = catalog.searchResults(**query)
        assert_that(results, has_length(notes))

        deleted = delete_entity_data(username)
        assert_that(deleted, is_(notes))

        results = catalog.searchResults(**query)
        assert_that(results, has_length(0))
