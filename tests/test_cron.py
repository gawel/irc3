# -*- coding: utf-8 -*-
from irc3.testing import BotTestCase
from irc3.testing import MagicMock
from irc3.plugins import cron
from irc3.compat import asyncio


class MyCron:

    def __init__(self, bot):
        self.bot = bot

    @cron.cron('* * * * * *')
    def method(self):
        return self.bot


@cron.cron('* * * * * *')
@asyncio.coroutine
def function(bot):
    return bot


class TestCron(BotTestCase):

    config = dict(includes=['irc3.plugins.cron'])

    def test_add_remove_cron(self):
        bot = self.callFTU()
        plugin = bot.get_plugin(cron.Crons)
        plugin.connection_made()
        callback = MagicMock()
        c = bot.add_cron('* * * * *', callback)
        assert c.handle is not None
        assert len(plugin) == 1
        assert not callback.called
        plugin.remove_cron(c)
        assert len(plugin) == 0

    def test_connection_made(self):
        bot = self.callFTU()
        bot.include(__name__)
        plugin = bot.get_plugin(cron.Crons)
        assert not plugin.started
        plugin.connection_made()
        assert plugin.started

    def test_reload(self):
        bot = self.callFTU()
        bot.include(__name__)
        plugin = bot.get_plugin(cron.Crons)
        assert len(plugin) == 2
        plugin.before_reload()
        assert len(plugin) == 0
        assert not plugin.started
        plugin.after_reload()
        assert plugin.started

    def test_callable(self):
        loop = asyncio.new_event_loop()
        bot = self.callFTU(loop=loop)
        bot.include(__name__)
        plugin = bot.get_plugin(cron.Crons)

        results = []

        f = asyncio.Future(loop=loop)

        def complete(future):
            results.append(future.result())
            if len(results) == 2:
                f.set_result(results)

        for c in plugin:
            asyncio.ensure_future(
                c.next(), loop=loop).add_done_callback(complete)

        loop.run_until_complete(f)
        assert results == [bot, bot]
