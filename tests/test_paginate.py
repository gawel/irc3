# -*- coding: utf-8 -*-
from irc3.testing import BotTestCase
from irc3.plugins import command


@command.command
def to_page(bot, mask, *args):
    """test command
        %%to_page
    """
    def iterator():
        for i in range(10):
            yield str(i)
    for m in bot.paginate(mask, iterator()):
        yield m


class TestPager(BotTestCase):

    name = 'irc3.plugins.pager'

    config = dict(includes=[name, __name__])

    def test_cmd(self):
        bot = self.callFTU(nick='foo')
        plugin = bot.get_plugin(command.Commands)
        self.assertEqual(len(plugin), 4, plugin)
        bot.dispatch(':bar!user@host PRIVMSG foo :!to_page')
        self.assertSent(['PRIVMSG bar :%s' % i for i in range(4)])
        bot.dispatch(':bar!user@host PRIVMSG foo :!more')
        self.assertSent(['PRIVMSG bar :%s' % i for i in range(4, 10)])
