# -*- coding: utf-8 -*-
from irc3.testing import BotTestCase
from irc3.plugins import command
from irc3.plugins import dcc
from irc3.compat import asyncio
from irc3 import utils
import tempfile
import unittest
import shutil
import codecs
import os


@command.command(permission='myperm',
                 show_in_help_list=False,
                 options_first=True)
@dcc.dcc_command(options_first=True)
def cmd(bot, *args):
    """Test command
        %%cmd
    """
    return 'Done'


@command.command
def cmd_view(bot, *args):
    """test command
        %%cmd_view
    """
    return 'Done'


@command.command
def cmd_arg(bot, *args):
    """test command

        %%cmd_arg <arg>
    """
    return 'Done'


class TestCommands(BotTestCase):

    name = 'irc3.plugins.command'
    guard = 'irc3.plugins.command.mask_based_policy'
    masks = 'irc3.plugins.command.masks'

    config = dict(includes=[name])

    def test_async_plugin(self):
        bot = self.callFTU(nick='foo', loop=asyncio.new_event_loop())
        bot.include('async_command')
        plugin = bot.get_plugin(command.Commands)
        mask = utils.IrcString('a@a.com')
        res = plugin.on_command('get', mask, mask.nick, data='')
        assert isinstance(res, asyncio.Task)
        res2 = plugin.on_command('get', mask, mask.nick, data='')
        assert res2 is None
        plugin.on_command('put', mask, mask.nick, data='xx yy')
        bot.loop.run_until_complete(res)
        assert res.result() == ['xx', 'yy']

    def test_help(self):
        bot = self.callFTU(nick='foo')
        plugin = bot.get_plugin(command.Commands)
        self.assertEqual(len(plugin), 2, plugin)
        bot.dispatch(':bar!user@host PRIVMSG foo :!help')
        self.assertSent(
            ['PRIVMSG bar :Available commands: !help, !ping'])

        bot.dispatch(':bar!user@host PRIVMSG #chan :!help')
        self.assertSent(
            ['PRIVMSG #chan :Available commands: !help, !ping'])

    def test_help_hides(self):
        bot = self.callFTU(nick='foo')
        bot.include(__name__)
        # For direct messages
        bot.dispatch(':bar!user@host PRIVMSG foo :!help')
        self.assertSent(['PRIVMSG bar :Available commands: '
                        '!cmd_arg, !cmd_view, !help, !ping'])
        # channel messages
        bot.dispatch(':bar!user@host PRIVMSG #chan :!help')
        self.assertSent(['PRIVMSG #chan :Available commands: '
                        '!cmd_arg, !cmd_view, !help, !ping'])

    def test_help_with_url(self):
        bot = self.callFTU(nick='foo', **{
            'irc3.plugins.command': dict(url='http://localhost/')})
        plugin = bot.get_plugin(command.Commands)
        self.assertEqual(len(plugin), 2, plugin)
        bot.dispatch(':bar!user@host PRIVMSG foo :!help')
        self.assertSent([
            'PRIVMSG bar :Available commands: !help, !ping',
            'PRIVMSG bar :Full help is available at http://localhost/',
        ])

    def test_print_help(self):
        bot = self.callFTU(nick='foo')
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        path = os.path.join(tmp, 'help.rst')
        with codecs.open(path, 'w', encoding='utf8') as fd:
            bot.print_help_page(file=fd)
        with codecs.open(path, encoding='utf8') as fd:
            self.assertIn('Available Commands', fd.read())

    def test_command_char(self):
        bot = self.callFTU(**{'irc3.plugins.command': {'cmd': '$'}})
        bot.dispatch(':bar!user@host PRIVMSG foo :$ping')
        self.assertSent(['NOTICE bar :PONG bar!'])

        bot = self.callFTU(**{'cmd': '$'})
        bot.dispatch(':bar!user@host PRIVMSG foo :$ping')
        self.assertSent(['NOTICE bar :PONG bar!'])

    def test_weird_chars(self):
        bot = self.callFTU(nick='foo', **{
            'irc3.plugins.command': dict(cmd='|')})
        plugin = bot.get_plugin(command.Commands)
        self.assertEqual(len(plugin), 2, plugin)
        bot.dispatch(':bar!user@host PRIVMSG foo :|help')
        self.assertSent(
            ['PRIVMSG bar :Available commands: |help, |ping'])

    def test_command_trailing_space(self):
        bot = self.callFTU(nick='foo')
        bot.dispatch(':bar!user@host PRIVMSG foo :!ping')
        bot.dispatch(':bar!user@host PRIVMSG foo :!ping ')
        bot.dispatch(':bar!user@host PRIVMSG foo :!ping  ')
        self.assertSent(
            ['NOTICE bar :PONG bar!']*3)

    def test_command_argument_space(self):
        bot = self.callFTU(nick='foo')
        bot.include(__name__)
        bot.dispatch(':bar!user@host PRIVMSG foo :!cmd_arg test')
        bot.dispatch(':bar!user@host PRIVMSG foo :!cmd_arg  test')
        bot.dispatch(':bar!user@host PRIVMSG foo :!cmd_arg   test')
        bot.dispatch(':bar!user@host PRIVMSG foo :!cmd_arg   test ')
        self.assertSent(['PRIVMSG bar :Done'] * 4)

    def test_private_command(self):
        bot = self.callFTU()
        bot.dispatch(':bar!user@host PRIVMSG nono :!ping')
        self.assertSent(['NOTICE bar :PONG bar!'])
        bot.dispatch(':bar!user@host PRIVMSG #chan :!ping')
        self.assertSent([
            "PRIVMSG bar :You can only use the 'ping' command in private."])

    def test_help_command(self):
        bot = self.callFTU()
        bot.dispatch(':bar!user@host PRIVMSG #chan :!help ping')
        self.assertSent(['PRIVMSG #chan :ping/pong', 'PRIVMSG #chan :!ping'])

    def test_help_command_with_bang(self):
        bot = self.callFTU()
        bot.dispatch(':bar!user@host PRIVMSG #chan :!help !ping')
        self.assertSent(['PRIVMSG #chan :ping/pong', 'PRIVMSG #chan :!ping'])

    def test_reconnect_command(self):
        self.patch_asyncio()
        bot = self.callFTU(includes=['irc3.plugins.core'])
        bot.include('irc3.plugins.command',
                    venusian_categories=bot.venusian_categories + [
                        'irc3.debug',
                    ])
        bot.dispatch(':bar!user@host PRIVMSG #chan :!reconnect')
        self.assertSent(['PING :10'])

    @unittest.skip('')
    def test_antiflood(self):
        bot = self.callFTU(async=True, **{self.name: dict(antiflood=True)})
        bot.dispatch(':bar!user@host PRIVMSG #chan :!help ping')
        self.assertSent(['PRIVMSG #chan :ping/pong', 'PRIVMSG #chan :!ping'])

        bot.dispatch(':bar!user@host PRIVMSG #chan :!help ping')
        self.assertSent(["NOTICE bar :Please be patient and don't flood me"])

        plugin = bot.get_plugin(command.Commands)
        plugin.handles[('help', '#chan')].set_result(True)
        bot.dispatch(':bar!user@host PRIVMSG #chan :!help ping')
        self.assertSent(['PRIVMSG #chan :ping/pong', 'PRIVMSG #chan :!ping'])

    def test_unicode(self):
        bot = self.callFTU(nick='nono')
        bot.dispatch(':bar!user@host PRIVMSG nono :!ping eé')
        self.assertSent(['PRIVMSG bar :Invalid arguments.'])

    def test_invalid_arguments(self):
        bot = self.callFTU(nick='nono')
        bot.dispatch(':bar!user@host PRIVMSG nono :!ping xx')
        self.assertSent(['PRIVMSG bar :Invalid arguments.'])

    def test_command_case_insensitive(self):
        bot = self.callFTU(nick='nono')
        bot.dispatch(':bar!user@host PRIVMSG nono :!PiNG')
        self.assertSent(['NOTICE bar :PONG bar!'])

    def test_command_case_sensitive(self):
        bot = self.callFTU(**{self.name: {'casesensitive': True}})
        bot.dispatch(':bar!user@host PRIVMSG nono :!PiNG')
        self.assertNothingSent()

    def test_permissions(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)

        bot = self.callFTU(**{
            'storage': 'json://%s/storage.json' % tmp,
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

        bot.dispatch(':local_adm!user@host PRIVMSG #chan :!cmd_view')
        self.assertSent(['PRIVMSG #chan :Done'])

        bot.include('irc3.plugins.storage')
        bot.db[self.name] = {
            'nobody!*': 'myperm view'
        }
        bot.dispatch(':nobody!user@host PRIVMSG #chan :!cmd')
        self.assertSent(['PRIVMSG #chan :Done'])
