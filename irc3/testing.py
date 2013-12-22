# -*- coding: utf-8 -*-
from unittest import TestCase
import irc3


class BotTestCase(TestCase):

    config = {'nick': 'nono'}

    def callFTU(self, **config):
        config = dict(self.config, **config)
        config['async'] = False
        self.lines = []
        klass = type('IrcBot', (irc3.IrcBot,), dict(send=self.send))
        return klass(**config)

    def send(self, data):
        self.lines.append(data.strip('\r\n'))

    def assertSent(self, lines):
        self.assertEqual(self.lines, lines)
        self.lines = []

    def assertInSent(self, lines):
        for line in lines:
            self.assertIn(line, self.lines)
