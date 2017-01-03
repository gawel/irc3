
# -*- coding: utf-8 -*-
from irc3 import testing


class TestServerUserList(testing.ServerTestCase):

    def test_ison(self):
        s = self.callFTU(clients=2)
        s.client1.dispatch('ISON client2 client4')
        self.assertSent(
            s.client1,
            ':irc.com 303 client1 :client2'
        )

    def test_whois(self):
        s = self.callFTU(clients=2)
        s.client1.dispatch('WHOIS client2')
        self.assertSent(
            s.client1,
            ":irc.com 311 client1 client2 uclient2 127.0.0.1 * :I'm client2"
        )

    def test_whois_err(self):
        s = self.callFTU(clients=1)
        s.client1.dispatch('WHOIS client2')
        self.assertSent(
            s.client1, ":irc.com 401 client1 client2 :No such nick/channel")

    def test_user_modes(self):
        s = self.callFTU(clients=1)

        for mode in 'iw':
            s.client1.dispatch('MODE client1 +' + mode)
            self.assertIn(mode, s.client1.modes)
            s.client1.dispatch('MODE client1 -' + mode)
            self.assertNotIn(mode, s.client1.modes)

        s.client1.dispatch('MODE client1 +s')
        self.assertSent(s.client1, ':irc.com 501 client1 :Unknown MODE flag')

    def test_userlist(self):
        s = self.callFTU(clients=0)
        self.assertEqual(len(s.nicks), 0)
        s.add_clients(amount=3)
        self.assertEqual(len(s.nicks), 3)
        s.client1.dispatch('JOIN #irc')
        s.client1.dispatch('JOIN #irc3')
        self.assertEqual(len(s.channels['#irc3']), 1)
        s.client2.dispatch('JOIN #irc3')
        self.assertEqual(len(s.channels['#irc3']), 2)
        self.assertSent(s.client1, ':{mask} JOIN #irc3', s.client2)
        self.assertNotSent(s.client3, ':{mask} JOIN #irc3', s.client2)

        s.client1.dispatch('KICK #irc3 client2 :Lamer!')
        self.assertEqual(len(s.channels['#irc3']), 1)
        self.assertSent(s.client2, ':{mask} KICK #irc3 :Lamer!', s.client1)
        self.assertNotSent(s.client3, ':{mask} KICK #irc3 :Lamer!', s.client1)

        s.client2.dispatch('JOIN #irc3')
        self.assertEqual(len(s.channels['#irc3']), 2)

        s.client1.dispatch('MODE #irc3 +v client2')
        self.assertSent(s.client2, ':{mask} MODE #irc3 +v client2', s.client1)
        self.assertNotSent(
            s.client3, ':{mask} MODE #irc3 +v client2', s.client1)

        s.client1.dispatch('NICK irc3')
        self.assertSent(s.client2, ':client1!uclient1@127.0.0.1 NICK irc3')
        self.assertNotSent(s.client3, ':client1!uclient1@127.0.0.1 NICK irc3')

        s.client3.dispatch('JOIN #irc')
        s.client1.dispatch('NICK client1')
        self.assertSent(s.client2, ':irc3!uclient1@127.0.0.1 NICK client1')
        self.assertSent(s.client3, ':irc3!uclient1@127.0.0.1 NICK client1')

        s.client2.dispatch('NICK client1')
        self.assertSent(
            s.client2,
            ':irc.com 433 client2 client1 :Nickname is already in use')

        s.client1.reset()
        s.client1.dispatch('NAMES #irc')
        self.assertSent(s.client1,
                        ':irc.com 353 client1 = #irc :client1 client3')
        s.client1.dispatch('WHOIS client2')
        self.assertSent(s.client1, ':irc.com 319 client1 :#irc3')

        s.client3.dispatch('PART #irc :Bye')
        self.assertSent(s.client1, ':{mask} PART #irc :Bye', s.client3)
        self.assertNotSent(s.client2, ':{mask} PART #irc :Bye', s.client3)
