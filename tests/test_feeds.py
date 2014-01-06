# -*- coding: utf-8 -*-
from irc3.testing import BotTestCase
from irc3.testing import MagicMock
import datetime
import tempfile
import shutil
import os


def hook(entries):
    return []


class Hook:

    def __init__(self, bot):
        pass

    def __call__(self, entries):
        return []


class TestFeeds(BotTestCase):

    name = 'irc3.plugins.feeds'

    def setUp(self):
        wd = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, wd)
        self.wd = os.path.join(wd, 'feeds')
        dt = datetime.datetime.now().strftime('%Y-%m-%dT%M:%M:OO-08:00')
        self.patch_requests(
            filename='tests/feed.atom',
            DATE=dt,
        )

    def callFTU(self, **kwargs):
        config = dict(
            directory=self.wd,
            irc3='http://xxx',
            channels='#irc3', **kwargs
        )
        config = {
            'includes': [self.name],
            self.name: config
        }
        return super(TestFeeds, self).callFTU(**config)

    def test_connection_made(self):
        bot = self.callFTU()
        bot.loop.call_later = MagicMock()
        bot.notify('connection_made')
        self.assertTrue(bot.loop.call_later.called)

    def test_feed(self):
        bot = self.callFTU()
        bot.feeds.update()
        self.assertSent([
            'PRIVMSG #irc3 :[irc3] coverage '
            'https://github.com/gawel/irc3/commit/'
            'ec82ae2c5f8b2954f0646a2177deb65ad9db712a'])
        bot.feeds.update()
        self.assertSent([])

    def test_hooked_feed(self):
        bot = self.callFTU(hook='tests.test_feeds.hook')
        bot.feeds.update()
        self.assertSent([])

    def test_hooked_feed_with_class(self):
        bot = self.callFTU(hook='tests.test_feeds.Hook')
        bot.feeds.update()
        self.assertSent([])

    def test_exception(self):
        bot = self.callFTU()
        bot.feeds.fetch = bot.feeds.parse = MagicMock(side_effect=KeyError())
        bot.feeds.update()
