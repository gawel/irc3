
# -*- coding: utf-8 -*-
from irc3.testing import BotTestCase


class TestUptime(BotTestCase):

    def test_uptime(self):
        bot = self.callFTU(includes=['irc3.plugins.uptime'])
        bot.notify('connection_made')
        bot.dispatch(':gawel!u@h PRIVMSG #chan :!uptime')
        self.assertSent(
            [('PRIVMSG #chan :Up since 0 days 0 hours 0 minutes. '
              'Connected since 0 days 0 hours 0 minutes')])
        bot.uptime.uptime -= 3600 * 54
        bot.uptime.connection_uptime -= 3600 * 13

        bot.dispatch(':gawel!u@h PRIVMSG foo :!uptime')
        self.assertSent(
            [('PRIVMSG foo :Up since 2 days 6 hours 0 minutes. '
              'Connected since 0 days 13 hours 0 minutes')])
