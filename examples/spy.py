# -*- coding: utf-8 -*-
from irc3.compat import asyncio
import irc3


@irc3.plugin
class Plugin(object):

    chater = None

    def __init__(self, context):
        self.log = context.log
        self.context = context
        self.channel = context.config.channel
        try:
            self.chater = context.config.chater
        except Exception:
            self.chater = None

    @irc3.event(irc3.rfc.CONNECTED)
    def connected(self, **kw):
        self.context.join(self.channel)

    @irc3.event(irc3.rfc.PRIVMSG)
    def on_privmsg(self, mask=None, data=None, **kw):
        print(self.chater, mask, data)
        if self.chater:
            self.chater.privmsg(self.chater.config.channel,
                                '{0}: {1}'.format(mask.nick, data))


def main():
    loop = asyncio.get_event_loop()
    config = {
        'loop': loop,
        'nick': 'chater',
        'channel': '#irc3',
        'host': 'irc.freenode.net',
        'debug': True,
        'verbose': True,
        'raw': True,
        'includes': ['spy'],
    }
    chater = irc3.IrcBot.from_config(config)
    chater.run(forever=False)
    config.update({
        'nick': 'spyer',
        'channel': '#irc3_dev',
        'chater': chater,
    })
    spyer = irc3.IrcBot.from_config(config)
    spyer.run(forever=False)
    print('serving')
    loop.run_forever()
