# -*- coding: utf-8 -*-
from irc3.testing import BotTestCase


class TestUserList(BotTestCase):

    def test_userlist(self):
        bot = self.callFTU(nick='foo')
        bot.include('irc3.plugins.core',
                    'irc3.plugins.userlist')
        plugin = bot.get_plugin('irc3.plugins.userlist.Userlist')

        bot.dispatch(':bar!u@b JOIN #foo')
        self.assertIn('bar', plugin.channels['#foo'])
        self.assertNotIn('bar', plugin.channels['#bar'])
        self.assertIn('bar', plugin.nicks)

        bot.dispatch(':bar!u@b JOIN #bar')
        self.assertIn('bar', plugin.channels['#bar'])
        self.assertIn('bar', plugin.nicks)

        bot.dispatch(':bar!u@b PART #foo')
        self.assertIn('bar', plugin.channels['#bar'])
        self.assertIn('bar', plugin.nicks)

        bot.dispatch(':bar!u@b QUIT :lksdlds')
        self.assertNotIn('bar', plugin.nicks)

        bot.dispatch(':serv 352 irc3 #chan ~user host serv bar H@ :Blah')
        self.assertIn('bar', plugin.channels['#chan'])
        self.assertIn('bar', plugin.nicks)

        bot.dispatch(':serv 353 irc3 = #chan2 :bar @gawel')
        self.assertIn('bar', plugin.channels['#chan2'])
        self.assertIn('gawel', plugin.channels['#chan2'])
        self.assertIn('gawel', plugin.nicks)

        bot.notify('connection_lost')
        self.assertEqual(len(plugin.nicks), 0)
        self.assertEqual(len(plugin.channels), 0)

        bot.dispatch(':serv 353 irc3 = #chan2 :bar @gawel')
        self.assertEqual(len(plugin.nicks), 2)
        self.assertEqual(len(plugin.channels), 1)

        bot.dispatch(':bar!u@h PART #chan2')
        self.assertEqual(len(plugin.nicks), 1)

        bot.dispatch(':foo!u@h PART #chan2')
        self.assertNotIn('#chan2', plugin.channels)

        bot.dispatch(':foo!u@h QUIT')
        self.assertEqual(len(plugin.nicks), 0)
