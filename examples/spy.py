# -*- coding: utf-8 -*-
import irc3


@irc3.plugin
class Plugin(object):

    chater = None

    def __init__(self, context):
        self.log = context.log
        self.context = context
        self.channel = context.config.channel

    @irc3.event(irc3.rfc.CONNECTED)
    def connected(self, **kw):
        chater = self.context.config.botnet['bot_chater']
        if chater is self.context:
            self.chater = None
            self.log.info("I'm a chater")
        else:
            self.chater = chater
            self.log.info("I'm a spyer")
        self.context.join(self.channel)

    @irc3.event(irc3.rfc.PRIVMSG)
    def on_privmsg(self, mask=None, data=None, **kw):
        print(self.chater, mask, data)
        if self.chater:
            self.chater.privmsg(self.chater.config.channel,
                                '{0}: {1}'.format(mask.nick, data))
