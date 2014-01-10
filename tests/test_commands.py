# -*- coding: utf-8 -*-
from irc3.testing import BotTestCase
from irc3.plugins import command


@command.command(permission='myperm')
def cmd(bot, *args):
    """Test command
        %%cmd
    """
    return 'Done'


@command.command(permission='view')
def cmd_view(bot, *args):
    """Test command
        %%cmd_view
    """
    return 'Done'


class TestCommands(BotTestCase):

    name = 'irc3.plugins.command'
    guard = 'irc3.plugins.command.mask_based_policy'
    masks = 'irc3.plugins.command.masks'

    config = dict(includes=[name])

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

    def test_permissions(self):
        bot = self.callFTU(**{
            self.name: dict(guard=self.guard),
            self.masks: {
                'adm!*': 'all_permissions',
                'local_adm!*': 'myperm view',
                '*': 'view',
            }
        })
        bot.include(__name__)
        bot.dispatch(':adm!user@host PRIVMSG #chan :!cmd')
        self.assertSent(['PRIVMSG #chan :Done'])

        bot.dispatch(':local_adm!user@host PRIVMSG #chan :!cmd')
        self.assertSent(['PRIVMSG #chan :Done'])

        bot.dispatch(':nobody!user@host PRIVMSG #chan :!cmd')
        self.assertSent([
            "PRIVMSG nobody :You are not allowed to use the 'cmd' command"])

        bot.dispatch(':nobody!user@host PRIVMSG #chan :!cmd_view')
        self.assertSent(['PRIVMSG #chan :Done'])
