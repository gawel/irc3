# -*- coding: utf-8 -*-
from irc3.testing import MagicMock
import pytest
import irc3


@pytest.fixture(scope='function')
def irc_conn(request):
    irc_conn = irc3.IrcConnection()
    irc_conn.encoding = 'utf8'
    irc_conn.factory = MagicMock()
    irc_conn.connection_made(MagicMock())
    return irc_conn


def test_buffer(irc_conn):
    irc_conn.data_received(b'message')
    assert irc_conn.queue.popleft() == 'message'


def test_no_buffer(irc_conn):
    irc_conn.data_received(b'message\r\n')
    irc_conn.factory.dispatch.assert_called_with('message')
    assert irc_conn.queue.popleft() == ''


def test_with_buffer(irc_conn):
    irc_conn.data_received(b'm1 ')
    irc_conn.data_received(b'm2 ')
    buf = irc_conn.queue.popleft()
    assert buf == 'm1 m2 '
    irc_conn.queue.append(buf)
    irc_conn.data_received(b'm3\r\nm4')
    irc_conn.factory.dispatch.assert_called_with('m1 m2 m3')
    assert irc_conn.queue.popleft() == 'm4'


def test_write(irc_conn):
    irc_conn.write('m1')
    irc_conn.transport.write.assert_called_with(b'm1\r\n')
    irc_conn.write('m2\r\n')
    irc_conn.transport.write.assert_called_with(b'm2\r\n')
