# -*- coding: utf-8 -*-
from irc3.testing import BotTestCase
from irc3.testing import patch
from irc3_plugins_test import test
import logging


class TestBot(BotTestCase):

    def test_config(self):
        bot = self.callFTU(verbose=True)
        self.assertEqual(bot.config.verbose, True)

    def test_include_twice(self):
        bot = self.callFTU()
        bot.include('irc3.plugins.log')
        bot.include('irc3.plugins.log')

    def test_plugin(self):
        bot = self.callFTU()
        bot.include('irc3.plugins.command')
        plugin = bot.get_plugin('irc3.plugins.command.Commands')
        self.assertTrue(plugin is not None)
        plugin = bot.get_plugin('irc3.plugins.command.Commands')
        self.assertTrue(plugin is not None)
        self.assertRaises(LookupError, bot.get_plugin,
                          'irc3.plugins.log.RawLog')

    def test_join(self):
        bot = self.callFTU(passwords=dict(foo='bar'))
        bot.join('#foo')
        self.assertSent(['JOIN #foo bar'])

    def test_message(self):
        bot = self.callFTU()
        bot.privmsg('gawel', 'Youhou!')
        self.assertSent(['PRIVMSG gawel :Youhou!'])
        bot.notice('gawel', 'Youhou!')
        self.assertSent(['NOTICE gawel :Youhou!'])
        bot.action('gawel', 'does a cool action')
        self.assertSent(['PRIVMSG gawel :\x01ACTION does a cool action\x01'])

    def test_long_message(self):
        bot = self.callFTU(max_length=8)
        message = 'How you doing?'
        bot.privmsg('gawel', message)
        self.assertSent([
            'PRIVMSG gawel :How you',
            'PRIVMSG gawel :doing?'
        ])

    def test_log(self):
        bot = self.callFTU(level='ERROR')
        bot.include('irc3.plugins.log', venusian_categories=['irc3.debug'])
        bot.dispatch('PING :youhou')
        bot.dispatch(':gawel!user@host PRIVMSG #chan :youhou')

    def test_logger(self):
        bot = self.callFTU(level='ERROR')
        log = logging.getLogger('irc.1')
        log.set_irc_targets(bot, '#log')
        log2 = logging.getLogger('irc.2')
        log2.set_irc_targets(bot, '#log2')
        log.info('foo')
        log2.info('foo2')
        self.assertSent([
            'PRIVMSG #log :INFO foo',
            'PRIVMSG #log2 :INFO foo2'
        ])
        self.assertNotEqual(
            log.handlers[0].targets,
            log2.handlers[0].targets
        )

    def test_quote(self):
        bot = self.callFTU()
        bot.include('irc3.plugins.command',
                    venusian_categories=bot.venusian_categories + [
                        'irc3.debug',
                    ])
        bot.dispatch(':gawel!user@host PRIVMSG nono :!quote who gawel')
        self.assertSent(['who gawel'])

    def test_ctcp(self):
        bot = self.callFTU()
        bot.ctcp('gawel', 'VERSION')
        self.assertSent(['PRIVMSG gawel :\x01VERSION\x01'])

    def test_server_config(self):
        bot = self.callFTU()
        bot.include('irc3.plugins.core')
        bot.notify('connection_made')
        bot.dispatch(':srv 005 foo STATUSMSG=+%@ ETRACE :are supported')
        bot.dispatch(':srv 376 foo :End of MOTD')
        self.assertEqual(bot.config['server_config']['STATUSMSG'], '+%@')
        self.assertTrue(bot.config['server_config']['ETRACE'])

    def test_ping(self):
        bot = self.callFTU()
        bot.include('irc3.plugins.core')
        bot.dispatch('PING :youhou')
        self.assertSent(['PONG :youhou'])

    def test_nick(self):
        bot = self.callFTU()
        bot.include('irc3.plugins.core')
        self.assertEqual(bot.nick, 'nono')
        bot.dispatch(':nono!user@host NICK :withcolon')
        self.assertEqual(bot.nick, 'withcolon')
        bot.dispatch(':withcolon!user@host NICK bar')
        self.assertEqual(bot.nick, 'bar')
        bot.dispatch(':h.net 432 * bar :xx')
        self.assertSent(['NICK bar_'])

    def test_mode(self):
        bot = self.callFTU()
        bot.mode('#foo', '+v', 'bar')
        self.assertSent(['MODE #foo +v bar'])

    def test_kick(self):
        bot = self.callFTU()
        bot.kick('#foo', 'bar')
        self.assertSent(['KICK #foo bar'])
        bot.kick('#foo', 'bar', 'bye')
        self.assertSent(['KICK #foo bar :bye'])

    def test_part(self):
        bot = self.callFTU()
        bot.part('#foo')
        self.assertSent(['PART #foo'])
        bot.part('#foo', 'bye')
        self.assertSent(['PART #foo :bye'])

    def test_quit(self):
        bot = self.callFTU()
        bot.quit()
        self.assertSent(['QUIT :bye'])
        bot.quit('foo')
        self.assertSent(['QUIT :foo'])

    @patch('time.sleep')
    def test_SIGINT(self, sleep):
        bot = self.callFTU()
        bot.SIGINT()
        self.assertTrue(sleep.called)
        self.assertTrue(bot.loop.stop.called)

    def test_SIGHUP(self):
        bot = self.callFTU()
        bot.SIGHUP()

    def test_pkg_resources_entry_points(self):
        config = dict(includes=['irc3.plugins.test'])
        bot = self.callFTU(**config)
        plugin = bot.get_plugin(test.test)
        self.assertEqual(plugin, 'success')

    def test_pkg_resources_entry_points_exception(self):
        config = dict(includes=['irc3.plugins.badtest'])
        with self.assertRaises(LookupError):
            self.callFTU(**config)
