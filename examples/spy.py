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
            self.chater = context.botnet['bot_chater']
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
