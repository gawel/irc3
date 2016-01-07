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
            # receiver joined the chan. offer a file
            conn = yield from self.context.dcc_send(mask, __file__)
            yield from conn.closed
            self.context.log.info('file sent to %s', mask.nick)

    @irc3.event(irc3.rfc.CTCP)
    @asyncio.coroutine
    def on_ctcp(self, mask=None, **kwargs):
        # parse ctcp message
        name, host, port, size = kwargs['ctcp'].split()[2:]
        self.context.log.info('%s is offering %s', mask.nick, name)
        # get the file
        conn = yield from self.context.create_task(self.context.dcc_get(
            mask, host, port, '/tmp/sent.py', int(size)))
        yield from conn.closed
        self.context.log.info('file received from %s', mask.nick)

        # end loop by setting future's result
        self.context.config.file_received.set_result(True)


def main():
    loop = asyncio.get_event_loop()

    # run a test server
    server = IrcServer.from_config(dict(
        loop=loop,
        servername='test',
        includes=['irc3d.plugins.core'],
    ))
    server.run(forever=False)

    cfg = dict(
        host='localhost',
        port=6667,
        nick='sender',
        includes=[__name__],
        loop=loop,
    )
    # this bot will send the file
    sender = irc3.IrcBot.from_config(cfg)
    sender.run(forever=False)

    file_received = asyncio.Future()

    def f():
        # this bot will receive the file
        receiver.run(forever=False)
    # assume receiver is created *after* sender
    receiver = irc3.IrcBot.from_config(cfg,
                                       nick='receiver',
                                       file_received=file_received)
    loop.call_later(.2, receiver.run, False)

    loop.run_until_complete(file_received)

if __name__ == '__main__':
    main()
