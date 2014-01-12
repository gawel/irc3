# -*- coding: utf-8 -*-
from irc3.testing import BotTestCase
from irc3.testing import patch
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
        bot.include('irc3.plugins.log')
        plugin = bot.get_plugin('irc3.plugins.log.RawLog')
        self.assertTrue(plugin is not None)
        self.assertRaises(LookupError, bot.get_plugin,
                          'irc3.plugins.command.Commands')

    def test_message(self):
        bot = self.callFTU()
        bot.privmsg('gawel', 'Youhou!')
        self.assertSent(['PRIVMSG gawel :Youhou!'])
        bot.notice('gawel', 'Youhou!')
        self.assertSent(['NOTICE gawel :Youhou!'])

    def test_long_message(self):
        bot = self.callFTU(max_length=7)
        message = 'How you doing?'
        bot.privmsg('gawel', message)
        self.assertSent([
            'PRIVMSG gawel :How you',
            'PRIVMSG gawel :doing?'
        ])

    def test_event(self):
        bot = self.callFTU()
        bot.include('irc3.plugins.core')
        self.assertIn('<event ', repr(list(bot.events.values())[0]))

    def test_bad_event(self):
        from irc3.dec import event
        self.assertRaises(Exception, event, '(.*')

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

    def test_ping(self):
        bot = self.callFTU()
        bot.include('irc3.plugins.core')
        bot.dispatch('PING :youhou')
        self.assertSent(['PONG youhou'])

    def test_nick(self):
        bot = self.callFTU()
        bot.include('irc3.plugins.core')
        self.assertEqual(bot.nick, 'nono')
        bot.dispatch(':nono!user@host NICK bar')
        self.assertEqual(bot.nick, 'bar')
        bot.dispatch(':h.net 432 * bar :xx')
        self.assertSent(['NICK bar_'])

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

    @patch('time.sleep')
    def test_SIGHUP(self, sleep):
        bot = self.callFTU()
        bot.SIGHUP()
        self.assertTrue(sleep.called)
        self.assertTrue(bot.protocol.transport.close.called)

    def test_autojoin(self):
        bot = self.callFTU(autojoins=['#foo'])
        bot.include('irc3.plugins.core')
        bot.dispatch(':hobana.freenode.net 376 irc3 :End of /MOTD command.')
        self.assertSent(['JOIN #foo'])

    def test_autojoin_without_diese(self):
        bot = self.callFTU(autojoins=['foo'])
        bot.include('irc3.plugins.core')
        bot.dispatch(':hobana.freenode.net 376 irc3 :End of /MOTD command.')
        self.assertSent(['JOIN #foo'])
