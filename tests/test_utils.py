# -*- coding: utf-8 -*-
from unittest import TestCase
from irc3.utils import IrcString
from irc3.utils import maybedotted
from irc3.utils import split_message
import irc3.plugins


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

        s = IrcString('*')
        self.assertTrue(s.is_server)

    def test_maybedotted(self):
        self.assertTrue(
            maybedotted('irc3.plugins') is irc3.plugins)
        self.assertTrue(
            maybedotted('irc3.utils.IrcString') is IrcString)
        self.assertTrue(
            maybedotted(IrcString) is IrcString)
        self.assertRaises(LookupError, maybedotted, 'irc3.none.none')
        self.assertRaises(LookupError, maybedotted, 'irc3.none')
        self.assertRaises(LookupError, maybedotted, None)
        self.assertRaises(LookupError, maybedotted, '')


class TestSplit(TestCase):
    def callFTU(self, messages, **kwargs):
        return list(split_message(' '.join(messages), 80))

    def test_split_message(self):
        messages = ['allo', 'http://' * 80]
        self.assertEqual(messages, self.callFTU(messages))
        messages = ['http://' * 80, 'allo allo', 'http://' * 80]
        self.assertEqual(messages, self.callFTU(messages))
        # nonbreaking space
        messages = ['allo http://' * 80]
        self.assertEqual(messages, self.callFTU(messages))
