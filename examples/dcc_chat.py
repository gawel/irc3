# -*- coding: utf-8 -*-
from irc3.compat import asyncio
from irc3d import IrcServer
import irc3


@irc3.plugin
class Plugin(object):

    def __init__(self, context):
        self.log = context.log
        self.context = context

    @irc3.event(irc3.rfc.CONNECTED)
    def connected(self, **kw):
        self.context.join('#dcc')

    @irc3.event(irc3.rfc.JOIN)
    @asyncio.coroutine
    def join(self, mask=None, **kw):
        if mask.nick != self.context.nick and mask.nick == 'receiver':
            # receiver joined the chan. offer a chat
            conn = yield from self.context.dcc_chat(mask)
            # wait for my buddy
            yield from conn.started
            # say hi
            conn.send_line('Hi!')
            yield from conn.closed
            self.context.log.info('chat with %s closed', mask.nick)

    @irc3.event(irc3.rfc.CTCP)
    @asyncio.coroutine
    def on_ctcp(self, mask=None, **kwargs):
        # parse ctcp message
        print(kwargs)
        host, port = kwargs['ctcp'].split()[3:]
        self.context.log.info('%s is offering a chat', mask.nick)
        # open the chat
        conn = yield from self.context.dcc_chat(mask, host, port)
        conn.send_line('youhou')
        # end the loop after a few seconds
        self.context.loop.call_later(1,
                                     self.context.config.end_chat.set_result,
                                     True)
        yield from conn.closed
        self.context.log.info('chat with %s closed', mask.nick)

    @irc3.dcc_event(r'(?P<data>.*)')
    def on_dcc(self, client=None, data=None):
        """event to catch everything in dcc chats"""
        self.context.log.info('%r sent %s', client, data)


def main():
    loop = asyncio.get_event_loop()

    # run a test server
    server = IrcServer.from_config(dict(
        loop=loop,
        servername='test',
        includes=['irc3d.plugins.core'],
    ))
    server.run(forever=False)

    end_chat = asyncio.Future()

    cfg = dict(
        host='localhost',
        port=6667,
        nick='sender',
        includes=['irc3.plugins.dcc', __name__],
        loop=loop,
        end_chat=end_chat,
    )
    # this bot will send the file
    sender = irc3.IrcBot.from_config(cfg)
    sender.run(forever=False)

    def f():
        # this bot will receive the file
        receiver.run(forever=False)
    # assume receiver is created *after* sender
    receiver = irc3.IrcBot.from_config(cfg, nick='receiver')
    loop.call_later(.2, receiver.run, False)

    loop.run_until_complete(end_chat)

if __name__ == '__main__':
    main()
