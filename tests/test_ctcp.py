# -*- coding: utf-8 -*-
from irc3.testing import BotTestCase
from irc3.plugins.ctcp import CTCP


class TestCTCP(BotTestCase):

    config = dict(includes=['irc3.plugins.ctcp'],
                  ctcp_max_replies=3,
                  ctcp=dict(foo='bar'))

    def test_ctcp(self):
        bot = self.callFTU(autojoins=['foo'])
        bot.dispatch(':gawel!user@host PRIVMSG irc3 :\x01FOO\x01')
        self.assertSent(['NOTICE gawel :\x01FOO bar\x01'])

    def test_ctcp_flood(self):
        bot = self.callFTU(autojoins=['foo'])
        plugin = bot.get_plugin(CTCP)

        bot.dispatch(':gawel!user@host PRIVMSG irc3 :\x01FOO\x01')
        self.assertTrue(plugin.handle is not None, plugin.handle)
        bot.dispatch(':gawel!user@host PRIVMSG irc3 :\x01FOO\x01')
        bot.dispatch(':gawel!user@host PRIVMSG irc3 :\x01FOO\x01')

        # flood
        bot.dispatch(':gawel!user@host PRIVMSG irc3 :\x01FOO\x01')
        bot.dispatch(':gawel!user@host PRIVMSG irc3 :\x01FOO\x01')
        bot.dispatch(':gawel!user@host PRIVMSG irc3 :\x01FOO\x01')
        bot.dispatch(':gawel!user@host PRIVMSG irc3 :\x01FOO\x01')
        self.assertSent(['NOTICE gawel :\x01FOO bar\x01'] * 3)
