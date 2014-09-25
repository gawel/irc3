# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from irc3 import testing
import irc3d


@irc3d.extend
def echo(self):
    return self


class TestServer(testing.ServerTestCase):

    def test_mock(self):
        s = self.callFTU(clients=2)
        self.assertEqual(len(s.clients), 2)

    def test_connection_lost(self):
        s = self.callFTU(clients=2)
        s.client1.connection_lost(None)
        self.assertEqual(len(s.nicks), 1)

    def test_log(self):
        s = self.callFTU(clients=2)
        s.include('irc3.plugins.log', venusian_categories=['irc3d.debug'])
        s.client1.dispatch('PING :yé')

    def test_extend(self):
        s = self.callFTU(clients=0)
        s.include(__name__)
        self.assertTrue(s.echo() is s)

    def test_unknow_command(self):
        s = self.callFTU(clients=1)
        s.client1.dispatch('EHLO')
        self.assertSent(
            s.client1, ':irc.com 421 client1 EHLO :Unknown command')

    def test_server_notice(self):
        s = self.callFTU(clients=1)
        s.notice(s.client1, 'test')
        self.assertSent(s.client1, ':irc.com NOTICE client1 :test')

    def test_broadcast(self):
        s = self.callFTU(clients=1)
        s.broadcast(s.client1, broadcast='Hi')

    def test_ping(self):
        s = self.callFTU(clients=1)
        s.client1.dispatch('PING xx')
        self.assertSent(s.client1, ':irc.com PONG irc.com :xx')

    def test_privmsg(self):
        s = self.callFTU(clients=3)
        s.client1.dispatch('JOIN #irc3')
        s.client2.dispatch('JOIN #irc3')

        s.client1.dispatch('PRIVMSG client3 :Hello client3!')
        self.assertSent(
            s.client3, ':{mask} PRIVMSG client3 :Hello client3!', s.client1)

        s.client1.dispatch('PRIVMSG #irc3 :Hello #irc3!')
        self.assertSent(
            s.client2, ':{mask} PRIVMSG #irc3 :Hello #irc3!', s.client1)
        self.assertNotSent(
            s.client3, ':{mask} PRIVMSG #irc3 :Hello #irc3!', s.client1)

        s.client1.dispatch('PRIVMSG #irc5 :Hello #irc5!')
        self.assertSent(
            s.client1, ':irc.com 401 client1 None :No such nick/channel')
