# -*- coding: utf-8 -*-
from irc3.testing import BotTestCase
from irc3.testing import MagicMock
from irc3.plugins import cron


class MyCron(object):

    def __init__(self, bot):
        pass

    @cron.cron('* * * * *')
    def raiser(self):
        raise RuntimeError()


def null_callback(bot):
    pass


class TestCron(BotTestCase):

    config = dict(includes=[])

    def setUp(self):
        cron.Cron.start_time = 0

    def test_cron(self):
        bot = self.callFTU()
        bot.loop = MagicMock()
        bot.include('mycrons')
        plugin = bot.get_plugin(cron.Crons)
        plugin.log.setLevel(1000)
        plugin.connection_made()
        self.assertEqual(len(plugin), 2, plugin)
        self.assertTrue(bot.loop.call_at.call_count, 2)

        bot.loop.reset_mock()
        plugin.call_cron(plugin[1])
        self.assertTrue(bot.loop.call_at.call_count, 1)

        self.assertIn('*/2', str(plugin[0]))

    def test_cron_raise(self):
        bot = self.callFTU()
        bot.loop = MagicMock()
        bot.include(__name__)
        plugin = bot.get_plugin(cron.Crons)
        plugin.log.setLevel(1000)
        plugin.connection_made()
        self.assertEqual(len(plugin), 1, plugin)
        self.assertTrue(bot.loop.call_at.call_count, 1)

        bot.loop.reset_mock()
        plugin.call_cron(plugin[0])
        self.assertTrue(bot.loop.call_at.call_count, 1)

    def test_add_remove_cron(self):
        bot = self.callFTU(includes=['irc3.plugins.cron'])
        plugin = bot.get_plugin(cron.Crons)
        callback = MagicMock()
        c = bot.add_cron('* * * * *', callback)
        self.assertEqual(len(plugin), 1, plugin)
        self.assertFalse(callback.called)
        plugin.started = True
        bot.remove_cron(uuid=c.uuid)
        bot.loop = MagicMock()
        c = bot.add_cron('* * * * *', callback)
        self.assertEqual(len(plugin), 2, plugin)
        self.assertTrue(bot.loop.call_at.called)
        bot.remove_cron(c)
