# -*- coding: utf-8 -*-
from irc3.testing import BotTestCase
from irc3.plugins.command import Commands


class TestBot(BotTestCase):

    def test_event(self):
        bot = self.callFTU()
        bot.include('irc3.plugins.core')
        self.assertIn('<event ', repr(bot.events[0]))

    def test_log(self):
        bot = self.callFTU()
        bot.include('irc3.plugins.log')
        bot.dispatch('PING :youhou')

    def test_ping(self):
        bot = self.callFTU()
        bot.include('irc3.plugins.core')
        bot.dispatch('PING :youhou')
        self.assertSent(['PONG youhou'])

    def test_nick(self):
        bot = self.callFTU()
        bot.include('irc3.plugins.core')
        self.assertEqual(bot.nick, 'foo')
        bot.dispatch(':foo!user@host NICK bar')
        self.assertEqual(bot.nick, 'bar')
        bot.dispatch(':h.net 432 * bar :xx')
        self.assertSent(['NICK bar_'])

    def test_part(self):
        bot = self.callFTU()
        bot.part('#foo')
        self.assertSent(['PART #foo'])
        bot.part('#foo', 'bye')
        self.assertSent(['PART #foo :bye'])

    def test_autojoin(self):
        bot = self.callFTU(autojoins=['#foo'])
        bot.include('irc3.plugins.core')
        bot.dispatch(':hobana.freenode.net 376 irc3 :End of /MOTD command.')
        self.assertSent(['JOIN #foo'])

    def test_command(self):
        bot = self.callFTU(nick='foo', **{'help.item_per_line': '6'})
        bot.include('irc3.plugins.core',
                    'irc3.plugins.command')
        plugin = bot.get_plugin(Commands)
        self.assertEqual(len(plugin), 2, plugin)
        bot.dispatch(':bar!user@host PRIVMSG foo :!help')
        self.assertSent(
            ['PRIVMSG bar :Available commands: !help, !ping'])

        bot.dispatch(':bar!user@host PRIVMSG #chan :!help')
        self.assertSent(
            ['PRIVMSG #chan :Available commands: !help, !ping'])

        cmd = plugin['help']
        for i in range(10, 25):
            plugin['cmd%s' % i] = cmd

        bot.dispatch(':bar!user@host PRIVMSG #chan :!help')
        self.assertSent(
            ['PRIVMSG #chan :Available commands: !cmd10, !cmd11, !cmd12',
             'PRIVMSG #chan :!cmd13, !cmd14, !cmd15, !cmd16, !cmd17, !cmd18',
             'PRIVMSG #chan :!cmd19, !cmd20, !cmd21, !cmd22, !cmd23, !cmd24',
             'PRIVMSG #chan :!help, !ping']
        )

        bot.dispatch(':bar!user@host PRIVMSG #chan :!ping')
        self.assertSent(['NOTICE bar :PONG bar!'])

        bot.dispatch(':bar!user@host PRIVMSG #chan :!help ping')
        self.assertSent(['PRIVMSG #chan :ping/pong', 'PRIVMSG #chan :!ping'])

        bot.dispatch(':bar!user@host PRIVMSG #chan :!ping xx')
        self.assertSent(['PRIVMSG #chan :Invalid arguments'])

    def test_userlist(self):
        bot = self.callFTU(nick='foo')
        bot.include('irc3.plugins.core',
                    'irc3.plugins.userlist')
        plugin = bot.get_plugin('userlist')

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
