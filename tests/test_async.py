# -*- coding: utf-8 -*-
import pytest


@pytest.mark.asyncio
def test_whois_fail(irc3_bot_factory):
    bot = irc3_bot_factory(includes=['irc3.plugins.async'])
    assert len(bot.registry.events_re['in']) == 0
    task = bot.async_cmds.whois(nick='gawel')
    assert len(bot.registry.events_re['in']) > 2
    bot.dispatch(':localhost 401 me gawel :No such nick')
    result = yield from task
    assert result['success'] is False
    assert len(bot.registry.events_re['in']) == 0


@pytest.mark.asyncio
def test_whois_success(irc3_bot_factory):
    bot = irc3_bot_factory(includes=['irc3.plugins.async'])
    assert len(bot.registry.events_re['in']) == 0
    task = bot.async_cmds.whois(nick='GaWel')
    assert len(bot.registry.events_re['in']) > 2
    bot.dispatch(':localhost 311 me gawel username localhost * :realname')
    bot.dispatch(':localhost 319 me gawel :@#irc3')
    bot.dispatch(':localhost 312 me gawel localhost :Paris, FR')
    bot.dispatch(':localhost 671 me gawel :is using a secure connection')
    bot.dispatch(':localhost 330 me gawel gawel :is logged in as')
    bot.dispatch(':localhost 318 me gawel :End')
    result = yield from task
    assert len(bot.registry.events_re['in']) == 0
    assert result['success']
    assert result['timeout'] is False
    assert result['username'] == 'username'
    assert result['realname'] == 'realname'


@pytest.mark.asyncio
def test_whois_timeout(irc3_bot_factory):
    bot = irc3_bot_factory(includes=['irc3.plugins.async'])
    assert len(bot.registry.events_re['in']) == 0
    task = bot.async_cmds.whois(nick='GaWel', timeout=.1)
    assert len(bot.registry.events_re['in']) > 2
    result = yield from task
    assert result['timeout'] is True


@pytest.mark.asyncio
def test_who_channel(irc3_bot_factory):
    bot = irc3_bot_factory(includes=['irc3.plugins.async'])
    assert len(bot.registry.events_re['in']) == 0
    task = bot.async_cmds.who('#irc3')
    assert len(bot.registry.events_re['in']) == 2
    bot.dispatch(
        ':card.freenode.net 352 nick #irc3 ~irc3 host1 srv1 irc3 H :0 bot')
    bot.dispatch(
        ':card.freenode.net 352 nick #irc3 ~gael host2 srv2 gawel H@ :1 g')
    bot.dispatch(':card.freenode.net 315 nick #irc3 :End of /WHO list.')
    result = yield from task
    assert result['timeout'] is False
    assert len(result['users']) == 2


@pytest.mark.asyncio
def test_who_channel_flags(irc3_bot_factory):
    bot = irc3_bot_factory(includes=['irc3.plugins.async'])
    assert len(bot.registry.events_re['in']) == 0
    task = bot.async_cmds.who('#irc3', 'ahinrsu')
    assert len(bot.registry.events_re['in']) == 2
    bot.dispatch(
        ':card.freenode.net 354 nick ~irc3 1.1.1.1 host1 srv1 irc3 0 :0 bot')
    bot.dispatch(
        ':card.freenode.net 354 nick ~gael 2.2.2.2 host2 srv2 gawel g :1 g')
    bot.dispatch(':card.freenode.net 315 nick #irc3 :End of /WHO list.')
    result = yield from task
    assert result['timeout'] is False
    assert len(result['users']) == 2
    # First user
    assert result['users'][0]['account'] is None
    assert result['users'][0]['host'] == 'host1'
    assert result['users'][0]['ip'] == '1.1.1.1'
    assert result['users'][0]['nick'] == 'irc3'
    assert result['users'][0]['realname'] == '0 bot'
    assert result['users'][0]['server'] == 'srv1'
    assert result['users'][0]['user'] == '~irc3'
    # Second user
    assert result['users'][1]['account'] == 'g'
    assert result['users'][1]['host'] == 'host2'
    assert result['users'][1]['ip'] == '2.2.2.2'
    assert result['users'][1]['nick'] == 'gawel'
    assert result['users'][1]['realname'] == '1 g'
    assert result['users'][1]['server'] == 'srv2'
    assert result['users'][1]['user'] == '~gael'


@pytest.mark.asyncio
def test_who_nick(irc3_bot_factory):
    bot = irc3_bot_factory(includes=['irc3.plugins.async'])
    assert len(bot.registry.events_re['in']) == 0
    task = bot.async_cmds.who('irc3')
    assert len(bot.registry.events_re['in']) == 2
    bot.dispatch(
        ':card.freenode.net 352 nick * ~irc3 host1 serv1 irc3 H :0 bot')
    bot.dispatch(':card.freenode.net 315 nick irc3 :End of /WHO list.')
    result = yield from task
    assert result['timeout'] is False
    assert result['hopcount'] == '0'


@pytest.mark.asyncio
def test_topic(irc3_bot_factory):
    bot = irc3_bot_factory(includes=['irc3.plugins.async'])
    assert len(bot.registry.events_re['in']) == 0
    task = bot.async_cmds.topic('#chan', topic='test', timeout=.1)
    assert len(bot.registry.events_re['in']) > 0
    bot.dispatch(':localhost TOPIC #chan :test')
    result = yield from task
    assert result['timeout'] is False
    assert result['topic'] == 'test'


@pytest.mark.asyncio
def test_no_topic(irc3_bot_factory):
    bot = irc3_bot_factory(includes=['irc3.plugins.async'])
    assert len(bot.registry.events_re['in']) == 0
    task = bot.async_cmds.topic('#chan', timeout=.1)
    assert len(bot.registry.events_re['in']) > 0
    bot.dispatch(':localhost 331 me #chan :Not topic')
    result = yield from task
    assert result['timeout'] is False
    assert result['topic'] is None


@pytest.mark.asyncio
def test_ison(irc3_bot_factory):
    bot = irc3_bot_factory(includes=['irc3.plugins.async'])
    assert len(bot.registry.events_re['in']) == 0
    task = bot.async_cmds.ison('GaWel', timeout=.1)
    assert len(bot.registry.events_re['in']) > 0
    bot.dispatch(':localhost 303 me :gawel')
    result = yield from task
    assert result['timeout'] is False
    assert result['names'] == ['gawel']


@pytest.mark.asyncio
def test_names(irc3_bot_factory):
    bot = irc3_bot_factory(includes=['irc3.plugins.async'])
    assert len(bot.registry.events_re['in']) == 0
    task = bot.async_cmds.names('#irc3')
    assert len(bot.registry.events_re['in']) == 2
    bot.dispatch(
        ':card.freenode.net 353 nick @ #irc3 :irc3 @gawel')
    bot.dispatch(
        ':card.freenode.net 353 nick @ #irc3 :+panoramisk')
    bot.dispatch(
        ':card.freenode.net 366 nick #irc3 :End of /NAMES list.')
    result = yield from task
    assert result['timeout'] is False
    assert len(result['names']) == 3


@pytest.mark.asyncio
def test_channel_bans(irc3_bot_factory):
    bot = irc3_bot_factory(includes=['irc3.plugins.async'])
    assert len(bot.registry.events_re['in']) == 0
    task = bot.async_cmds.channel_bans('#irc3')
    assert len(bot.registry.events_re['in']) == 2
    bot.dispatch(':card.freenode.net 367 nick #irc3 *!*@host irc3 1494621383')
    bot.dispatch(':card.freenode.net 368 nick #irc3 :End of Channel Ban List')
    result = yield from task
    assert result['timeout'] is False
    assert len(result['bans']) == 1
    assert result['bans'][0]['mask'] == '*!*@host'
    assert result['bans'][0]['user'] == 'irc3'
    assert result['bans'][0]['timestamp'] == 1494621383


@pytest.mark.asyncio
def test_ctcp(irc3_bot_factory):
    bot = irc3_bot_factory(includes=['irc3.plugins.async'])
    assert len(bot.registry.events_re['in']) == 0
    task = bot.async_cmds.ctcp_async('irc3', 'VERSION')
    assert len(bot.registry.events_re['in']) == 2
    bot.dispatch(':irc3!irc3@host1 NOTICE nick :\x01VERSION IRC3 Library\x01')
    result = yield from task
    assert result['timeout'] is False
    assert result['mask'] == 'irc3!irc3@host1'
    assert result['ctcp'] == 'VERSION'
    assert result['reply'] == 'IRC3 Library'
