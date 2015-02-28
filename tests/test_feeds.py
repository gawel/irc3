# -*- coding: utf-8 -*-
from irc3.testing import BotTestCase
from irc3.testing import MagicMock
from irc3.testing import asyncio
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


class Dispatcher:

    def __init__(self, bot):
        self.loop = bot.loop
        self.reset()

    def reset(self):
        self.future = asyncio.Future(loop=self.loop)
        return self.future

    def __call__(self, messages):
        self.future.set_result(list(messages))


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
        loop = kwargs.pop('loop', None)
        config = dict(
            directory=self.wd,
            irc3='http://xxx',
            dispatcher='tests.test_feeds.Dispatcher',
            channels='#irc3', **kwargs
        )
        config = {
            'includes': [self.name],
            self.name: config
        }
        if loop:
            config.update(loop=loop)
        return super(TestFeeds, self).callFTU(**config)

    def test_connection_made(self):
        bot = self.callFTU()
        bot.loop.call_later = MagicMock()
        bot.notify('connection_made')
        self.assertTrue(bot.loop.call_later.called)

    def test_feed(self):
        bot = self.callFTU(loop=asyncio.new_event_loop())
        future = bot.feeds.dispatcher.reset()
        bot.feeds.update()
        bot.loop.run_until_complete(future)
        assert future.result() == [
            ('#irc3', '[irc3] coverage https://github.com/gawel/irc3/commit/'
                      'ec82ae2c5f8b2954f0646a2177deb65ad9db712a')]
        bot = self.callFTU(loop=asyncio.new_event_loop())
        future = bot.feeds.dispatcher.reset()
        bot.feeds.update()
        bot.loop.run_until_complete(future)
        assert future.result() == []

    def test_hooked_feed(self):
        bot = self.callFTU(hook='tests.test_feeds.hook',
                           loop=asyncio.new_event_loop())
        future = bot.feeds.dispatcher.reset()
        bot.feeds.update()
        bot.loop.run_until_complete(future)
        assert future.result() == []

    def test_hooked_feed_with_class(self):
        bot = self.callFTU(hook='tests.test_feeds.Hook',
                           loop=asyncio.new_event_loop())
        assert isinstance(bot.feeds.hook, Hook)
        future = bot.feeds.dispatcher.reset()
        bot.feeds.update()
        bot.loop.run_until_complete(future)
        assert future.result() == []
