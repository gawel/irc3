# -*- coding: utf-8 -*-
from irc3.testing import BotTestCase
from irc3.plugins import command


class TestCommands(BotTestCase):

    config = dict(
        includes=('irc3.plugins.core',
                  'irc3.plugins.command'))

    def test_help(self):
        bot = self.callFTU(nick='foo', **{'help.item_per_line': '6'})
        plugin = bot.get_plugin(command.Commands)
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

    def test_command_char(self):
        bot = self.callFTU(**{'irc3.plugins.command': {'cmd': '\$'}})
        bot.dispatch(':bar!user@host PRIVMSG foo :$ping')
        self.assertSent(['NOTICE bar :PONG bar!'])

    def test_private_command(self):
        bot = self.callFTU()
        bot.dispatch(':bar!user@host PRIVMSG foo :!ping')
        self.assertSent(['NOTICE bar :PONG bar!'])

    def test_public_command(self):
        bot = self.callFTU()
        bot.dispatch(':bar!user@host PRIVMSG #chan :!ping')
        self.assertSent(['NOTICE bar :PONG bar!'])

    def test_help_command(self):
        bot = self.callFTU()
        bot.dispatch(':bar!user@host PRIVMSG #chan :!help ping')
        self.assertSent(['PRIVMSG #chan :ping/pong', 'PRIVMSG #chan :!ping'])

    def test_invalid_arguments(self):
        bot = self.callFTU()
        bot.dispatch(':bar!user@host PRIVMSG #chan :!ping xx')
        self.assertSent(['PRIVMSG #chan :Invalid arguments'])
