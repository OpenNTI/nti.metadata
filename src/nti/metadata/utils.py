#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from nti.dataserver.metadata_index import IX_CREATOR
from nti.dataserver.metadata_index import IX_TAGGEDTO
from nti.dataserver.metadata_index import IX_SHAREDWITH
from nti.dataserver.metadata_index import IX_REVSHAREDWITH
from nti.dataserver.metadata_index import IX_REPLIES_TO_CREATOR

from nti.zope_catalog.interfaces import IKeywordIndex

def delete_entity_metadata(catalog, username):
    result = 0
    if catalog is not None:
        username = username.lower()
        index = catalog[IX_CREATOR]
        query = {IX_CREATOR: {'any_of': (username,)}}
        results = catalog.searchResults(**query)
        for uid in results.uids:
            index.unindex_doc(uid)
            result += 1
    return result


def clear_replies_to_creator(catalog, username):
    """
    When a creator is removed, all of the things that were direct
    replies to that creator are now \"orphans\", with a value
    for ``inReplyTo``. We clear out the index entry for ``repliesToCreator``
    for this entity in that case.

    The same scenario holds for things that were shared directly
    to that user.
    """

    if catalog is None:
        # Not installed yet
        return

    # These we can simply remove, this creator doesn't exist anymore
    for ix_name in (IX_REPLIES_TO_CREATOR, IX_TAGGEDTO):
        index = catalog[ix_name]
        query = {ix_name: {'any_of': (username,)}}
        results = catalog.searchResults(**query)
        for uid in results.uids:
            index.unindex_doc(uid)

    # These, though, may still be shared, so we need to reindex them
    index = catalog[IX_SHAREDWITH]
    results = catalog.searchResults(sharedWith={'all_of': (username,)})
    intid_util = results.uidutil
    uids = list(results.uids or ())
    for uid in uids:
        obj = intid_util.queryObject(uid)
        if obj is not None:
            index.index_doc(uid, obj)

    index = catalog[IX_REVSHAREDWITH]
    if IKeywordIndex.providedBy(index):
        index.remove_words((username,))
