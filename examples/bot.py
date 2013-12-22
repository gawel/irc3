# -*- coding: utf-8 -*-
import irc3
from irc3.plugins.command import command
from irc3 import config
import logging.config


@command
def quote(bot, mask, target, args):
    """send quote to the server

        %%quote <args>...
    """
    msg = ' '.join(args['<args>'])
    bot.log.info('quote> %r', msg)
    bot.send(msg)


def main():
    logging.config.dictConfig(config.LOGGING)
    irc3.IrcBot(
        nick='irc3', autojoins=['#irc3'],
        host='irc.freenode.net', port=7000, ssl=True,
        includes=[
            'irc3.plugins.core',
            'irc3.plugins.log',
            'irc3.plugins.userlist',
            'irc3.plugins.command',
            'irc3.plugins.human',
            __name__,
        ]).run()

if __name__ == '__main__':
    main()
