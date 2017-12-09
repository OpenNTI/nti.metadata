#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

import unittest

from zope.dottedname import resolve as dottedname


class TestImport(unittest.TestCase):

    def test_import_interfaces(self):
        dottedname.resolve('nti.metadata.interfaces')

    def test_import_queues(self):
        dottedname.resolve('nti.metadata.queue')
