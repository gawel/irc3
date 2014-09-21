# -*- coding: utf-8 -*-
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

    def test_extend(self):
        s = self.callFTU(clients=0)
        s.include(__name__)
        self.assertTrue(s.echo() is s)

    def test_server_notice(self):
        s = self.callFTU(clients=1)
        s.notice(s.client1, 'test')
        self.assertSent(s.client1, ':127.0.0.1 NOTICE client1 :test')

    def test_ping(self):
        s = self.callFTU(clients=1)
        s.client1.dispatch('PING xx')
        self.assertSent(s.client1, ':127.0.0.1 PONG 127.0.0.1 :xx')

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
