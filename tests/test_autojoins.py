# -*- coding: utf-8 -*-
from irc3.testing import BotTestCase


class TestAutojoin(BotTestCase):

    def test_autojoin_without_diese(self):
        bot = self.callFTU(autojoins=['foo'])
        bot.include('irc3.plugins.core')
        bot.dispatch(':hobana.freenode.net 376 irc3 :End of /MOTD command.')
        self.assertSent(['JOIN #foo'])

    def test_autojoin(self):
        bot = self.callFTU(autojoins=['#foo'])
        bot.include('irc3.plugins.core')
        bot.dispatch(':hobana.freenode.net 376 irc3 :End of /MOTD command.')
        self.assertSent(['JOIN #foo'])

        bot.dispatch(':kicker!k@k KICK #foo irc3')
        self.assertSent(['JOIN #foo'])

        bot.dispatch(':kicker!k@k KICK #foo irc3 :bastard!')
        self.assertSent(['JOIN #foo'])

        bot.dispatch(':server 473 irc3 #foo :You are banned')
        self.assertSent(['JOIN #foo'])
