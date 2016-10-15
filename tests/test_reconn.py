# -*- coding: utf-8 -*-
import pytest
import irc3
import irc3d
from irc3.compat import asyncio


@irc3.plugin
class P:

    connections_made = []

    def __init__(self, bot):
        self.bot = bot

    def connection_made(self, *args, **kwargs):
        self.bot.log.info('P.connection_made')
        self.ready.set_result(True)
        self.connections_made.append(1)


@pytest.mark.asyncio
def test_reconn(irc3_bot_factory):
    cfg = {'verbose': True, 'debug': True}
    bot = irc3_bot_factory(includes=[__name__], **cfg)
    cfg['loop'] = bot.loop
    server = irc3d.IrcServer.from_config(cfg)

    P.ready = asyncio.Future(loop=bot.loop)
    assert len(P.connections_made) == 0

    server.run(forever=False)
    bot.run(forever=False)

    yield from P.ready
    P.ready = asyncio.Future(loop=bot.loop)

    assert len(P.connections_made) == 1

    for uid, client in server.clients.items():
        client.transport.close()
        print(uid, client)
    yield from P.ready
    P.ready = asyncio.Future(loop=bot.loop)

    assert len(P.connections_made) == 2
