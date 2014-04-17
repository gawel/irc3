# -*- coding: utf-8 -*-
import asyncio
import irc3


@irc3.event(irc3.rfc.JOIN)
def greetings(bot, mask=None, channel=None, **kw):
    if not mask.nick.startswith(bot.nick):
        bot.privmsg(channel, '%s: Hi dude!' % mask.nick)


def main():
    loop = asyncio.get_event_loop()

    config = dict(
        autojoins=['#irc3'],
        host='irc.freenode.net', port=7000, ssl=True,
        timeout=30,
        includes=[
            'irc3.plugins.core',
            'irc3.plugins.human',
            __name__,  # this register this module
        ],
        loop=loop)

    # instanciate two bot
    irc3.IrcBot(nick='bobirc', **config).run(forever=False)
    irc3.IrcBot(nick='jackyrc', **config).run(forever=False)

    loop.run_forever()

if __name__ == '__main__':
    main()
