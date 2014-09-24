# -*- coding: utf-8 -*-
import random
from irc3.compat import asyncio
from irc3d import IrcServer
import irc3


@irc3.plugin
class Plugin(object):

    def __init__(self, context):
        self.log = context.log
        self.context = context
        self.name = context.config.name
        self.channel = '#' + context.config.channel

    @irc3.event(irc3.rfc.CONNECTED)
    def connected(self, **kw):
        self.context.join(self.channel)

    def msg(self):
        s = ' '.join([self.name for i in range(random.randint(1, 10))])
        s += random.choice([' ?', '', ' !', ' #@!', ' '])
        self.context.privmsg(self.channel, s)
        self.context.loop.call_later(
            random.randint(3, 20), self.msg)

    @irc3.event(irc3.rfc.JOIN)
    def join(self, mask=None, **kw):
        if mask.nick == self.context.nick:
            self.context.loop.call_later(
                random.randint(3, 20), self.msg)


def main():
    loop = asyncio.get_event_loop()

    server = IrcServer.from_argv(loop=loop)
    bot = irc3.IrcBot.from_argv(loop=loop)

    def factory(i):
        irc3.IrcBot.from_argv(
            loop=loop, i=i,
            nick=bot.nick + str(i),
            realname=bot.config.realname + str(i),
        )

    for i in range(1, server.config.client_amount):
        loop.call_later(.1 * i, factory, i)

    loop.run_forever()
