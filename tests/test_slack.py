# -*- coding: utf-8 -*-
import pytest
from irc3.plugins import slack

pytestmark = pytest.mark.asyncio


async def test_simple_matches(irc3_bot_factory):
    bot = irc3_bot_factory(includes=['irc3.plugins.slack'])
    plugin = bot.get_plugin(slack.Slack)
    setattr(plugin, 'config', {'token': 'xoxp-faketoken'})
    assert '' == await plugin.parse_text('\n')
    assert '' == await plugin.parse_text('\r\n')
    assert '' == await plugin.parse_text('\r')
    assert '@channel' == await plugin.parse_text('<!channel>')
    assert '@group' == await plugin.parse_text('<!group>')
    assert '@everyone' == await plugin.parse_text('<!everyone>')
    assert '<' == await plugin.parse_text('&lt')
    assert '>' == await plugin.parse_text('&gt')
    assert '&' == await plugin.parse_text('&amp')
    assert 'daniel' == await plugin.parse_text('<WHATEVER|daniel>')


async def test_channel_matches(irc3_bot_factory):
    bot = irc3_bot_factory(includes=['irc3.plugins.slack'])
    plugin = bot.get_plugin(slack.Slack)
    setattr(plugin, 'config', {'token': 'xoxp-faketoken'})

    async def api_call(self, method, date=None):
        return ({'channel': {'name': 'testchannel'}})

    plugin.api_call = api_call
    assert '#testchannel' == await plugin.parse_text('<#C12345>')
    assert 'channel' == await plugin.parse_text('<#C12345|channel>')


async def test_user_matches(irc3_bot_factory):
    bot = irc3_bot_factory(includes=['irc3.plugins.slack'])
    plugin = bot.get_plugin(slack.Slack)
    setattr(plugin, 'config', {'token': 'xoxp-faketoken'})

    async def api_call(self, method, date=None):
        return ({'user': {'name': 'daniel'}})

    plugin.api_call = api_call
    assert '@daniel' == await plugin.parse_text('<@U12345>')
    assert 'user' == await plugin.parse_text('<@U12345|user>')


async def test_emoji_matches(irc3_bot_factory):
    bot = irc3_bot_factory(includes=['irc3.plugins.slack'])
    plugin = bot.get_plugin(slack.Slack)
    setattr(plugin, 'config', {'token': 'xoxp-faketoken'})
    assert ':-)' == await plugin.parse_text(':smiley:')
    assert ':@' == await plugin.parse_text(':rage:')
