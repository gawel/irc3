# -*- coding: utf-8 -*-
from irc3.testing import BotTestCase
from irc3.plugins.autojoins import AutoJoins


class TestAutojoin(BotTestCase):

    def test_autojoin_without_diese(self):
        bot = self.callFTU(autojoins=['foo'])
        bot.notify('connection_made')

        bot.dispatch(':hobana.freenode.net 376 irc3 :End of /MOTD command.')
        self.assertSent(['JOIN #foo'])

        bot.dispatch(':hobana.freenode.net 376 irc3 :End of /MOTD command.')
        self.assertSent([])

    def test_nomotd_events_removed(self):
        bot = self.callFTU(autojoins=['#foo'])
        bot.notify('connection_made')

        bot.dispatch(':hobana.freenode.net 422 irc3 :No MOTD.')
        self.assertSent(['JOIN #foo'])

        bot.dispatch(':hobana.freenode.net 422 irc3 :No MOTD.')
        self.assertSent([])

    def test_autojoin_nomotd(self):
        bot = self.callFTU(autojoins=['#foo'])
        bot.notify('connection_made')

        bot.dispatch(':hobana.freenode.net 422 irc3 :No MOTD.')
        self.assertSent(['JOIN #foo'])

    def test_autojoin(self):
        bot = self.callFTU(autojoins=['#foo'])
        bot.notify('connection_made')

        bot.dispatch(':hobana.freenode.net 376 irc3 :End of /MOTD command.')
        self.assertSent(['JOIN #foo'])

        bot.dispatch(':kicker!k@k KICK #foo irc3')
        self.assertSent(['JOIN #foo'])

        bot.dispatch(':kicker!k@k KICK #foo irc3 :bastard!')
        self.assertSent(['JOIN #foo'])

        plugin = bot.get_plugin(AutoJoins)
        self.assertEqual(plugin.handles, {})
        bot.dispatch(':server 473 irc3 #foo :You are banned')
        self.assertSent(['JOIN #foo'])
        self.assertIn('#foo', plugin.handles)
        self.assertEqual(2, plugin.handles['#foo'][0])

        # assume it doesn't break when a timeout is set
        bot.dispatch(':server 473 irc3 #foo :You are banned')
        self.assertSent(['JOIN #foo'])
        self.assertEqual(8, plugin.handles['#foo'][0])

        bot.dispatch(':kicker!k@k KICK #foo irc3 :bastard!')
        self.assertSent(['JOIN #foo'])
        self.assertNotIn('#foo', plugin.handles)

        bot.notify('connection_lost')
