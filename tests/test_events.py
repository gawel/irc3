# -*- coding: utf-8 -*-
from irc3.testing import BotTestCase
import irc3


@irc3.event(irc3.rfc.PRIVMSG)
def msg1(bot, **kwargs):
    bot.privmsg('#irc3', 'msg1')


@irc3.event(irc3.rfc.PRIVMSG)
def msg2(bot, **kwargs):
    bot.privmsg('#irc3', 'msg2')


@irc3.event(r'PRIVMSG (?P<target>[^#]+) :(?P<data>.*)', iotype='out')
def msg3(bot, target=None, data=None):
    bot.privmsg('#irc3', '<{0}> {1}: {2}'.format(bot.nick, target, data))


class TestEvents(BotTestCase):

    def test_event(self):
        bot = self.callFTU()
        bot.include('irc3.plugins.core')
        self.assertIn('<bound event ',
                      repr(list(bot.events['in'].values())[0]))

    def test_bad_event(self):
        self.assertRaises(Exception, irc3.event, '(.*')

    def test_not_include_twice(self):
        bot = self.callFTU()
        bot.include(__name__)
        bot.include(__name__)
        bot.dispatch(':g!g@g PRIVMSG #irc3 :allo')
        self.assertSent(['PRIVMSG #irc3 :msg1', 'PRIVMSG #irc3 :msg2'])

    def test_out_event(self):
        bot = self.callFTU()
        bot.include(__name__)
        bot.privmsg('foo', 'Hi!')
        self.assertSent([
            'PRIVMSG foo :Hi!',
            'PRIVMSG #irc3 :<nono> foo: Hi!',
        ])
