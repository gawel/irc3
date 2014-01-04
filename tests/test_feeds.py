# -*- coding: utf-8 -*-
from irc3.testing import BotTestCase
import datetime
import tempfile
import shutil
import os


def hook(i, feed, entry):
    return None


class Hook:

    def __init__(self, bot):
        pass

    def __call__(self, i, feed, entry):
        return None


class TestFeeds(BotTestCase):

    name = 'irc3.plugins.feeds'

    def setUp(self):
        wd = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, wd)
        self.wd = os.path.join(wd, 'feeds')

    def copyfile(self):
        dt = datetime.datetime.now().strftime('%Y-%m-%dT%M:%M:OO-08:00')
        with open(self.feed, 'w') as fd:
            with open('tests/feed.atom', 'r') as feed:
                fd.write(feed.read().replace('DATE', dt))

    def test_feed(self):
        config = dict(directory=self.wd,
                      irc3='http://xxx',
                      channels='irc3')
        bot = self.callFTU(includes=[self.name], **{
            self.name: config})
        self.feed = bot.feeds.feeds['irc3']['filenames'][0]
        self.copyfile()
        bot.feeds.update()
        self.assertSent([
            'PRIVMSG #irc3 :[irc3] coverage '
            'https://github.com/gawel/irc3/commit/'
            'ec82ae2c5f8b2954f0646a2177deb65ad9db712a'])
        bot.feeds.update()
        self.assertSent([])

    def test_hooked_feed(self):
        config = dict(directory=self.wd,
                      irc3='http://xxx#irc3',
                      hook='tests.test_feeds.hook')
        bot = self.callFTU(includes=[self.name], **{
            self.name: config})
        self.feed = bot.feeds.feeds['irc3']['filenames'][0]
        self.copyfile()
        bot.feeds.update()
        self.assertSent([])

    def test_hooked_feed_with_class(self):
        config = dict(directory=self.wd,
                      irc3='http://xxx#irc3',
                      hook='tests.test_feeds.Hook')
        bot = self.callFTU(includes=[self.name], **{
            self.name: config})
        self.feed = bot.feeds.feeds['irc3']['filenames'][0]
        self.copyfile()
        bot.feeds.update()
        self.assertSent([])
