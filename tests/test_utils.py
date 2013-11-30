# -*- coding: utf-8 -*-
from unittest import TestCase
from irc3.utils import IrcString


class TestUtils(TestCase):

    def test_ircstring(self):
        s = IrcString('nick')
        self.assertTrue(s.is_nick)
        self.assertEqual(s.nick, 'nick')
        self.assertEqual(s.host, None)

        s = IrcString('nick!user@host')
        self.assertTrue(s.is_user)
        self.assertTrue(s.is_nick)
        self.assertEqual(s.nick, 'nick')
        self.assertEqual(s.host, 'user@host')

        s = IrcString('#chan')
        self.assertTrue(s.is_channel)
        s = IrcString('&chan')
        self.assertTrue(s.is_channel)
