# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest
from irc3.testing import MagicMock
import irc3


class TestProtocol(unittest.TestCase):

    def callFTU(self):
        conn = irc3.IrcConnection()
        conn.encoding = 'utf8'
        conn.factory = MagicMock()
        conn.connection_made(MagicMock())
        return conn

    def test_buffer(self):
        conn = self.callFTU()
        conn.data_received(b'message')
        self.assertEqual(conn.queue.popleft(), 'message')

    def test_no_buffer(self):
        conn = self.callFTU()
        conn.data_received(b'message\r\n')
        conn.factory.dispatch.assert_called_with('message')
        self.assertEqual(conn.queue.popleft(), '')

    def test_with_buffer(self):
        conn = self.callFTU()
        conn.data_received(b'm1 ')
        conn.data_received(b'm2 ')
        buf = conn.queue.popleft()
        self.assertEqual(buf, 'm1 m2 ')
        conn.queue.append(buf)
        conn.data_received(b'm3\r\nm4')
        conn.factory.dispatch.assert_called_with('m1 m2 m3')
        self.assertEqual(conn.queue.popleft(), 'm4')

    def test_write(self):
        conn = self.callFTU()
        conn.write('m1')
        conn.transport.write.assert_called_with(b'm1\r\n')
        conn.write('m2\r\n')
        conn.transport.write.assert_called_with(b'm2\r\n')
        conn.write(b'm3\r\n')
        conn.transport.write.assert_called_with(b'm3\r\n')
