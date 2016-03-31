# -*- coding: utf-8 -*-
import os
import irc3
import logging
from irc3 import asyncio
from functools import partial
from irc3.compat import Queue
__doc__ = '''
==========================================
:mod:`irc3.plugins.fifo` Fifo plugin
==========================================

Allow to cat something to a channel using Unix's fifo

..
    >>> from irc3.testing import IrcBot
    >>> from irc3.testing import ini2config
    >>> import shutil
    >>> import os
    >>> try:
    ...     shutil.rmtree('/tmp/run/irc3')
    ... except:
    ...     pass

Usage::

    >>> config = ini2config("""
    ... [bot]
    ... includes =
    ...     irc3.plugins.fifo
    ... [irc3.plugins.fifo]
    ... runpath = /tmp/run/irc3
    ... """)
    >>> bot = IrcBot(**config)

When your bot will join a channel it will create a fifo::

    >>> bot.test(':irc3!user@host JOIN #channel')
    >>> print(os.listdir('/tmp/run/irc3'))
    ['channel']

You'll be able to print stuff to a channel from a shell::

    $ cat /etc/passwd > /tmp/run/irc3/channel
'''


@irc3.plugin
class Fifo(object):

    def __init__(self, context):
        self.log = logging.getLogger(__name__)
        self.context = context
        self.config = self.context.config[__name__]
        self.send_blank_line = self.config.get('send_blank_line', True)

        self.runpath = self.config.get('runpath', '/run/irc3')
        if not os.path.exists(self.runpath):
            os.makedirs(self.runpath)

        self.loop = self.context.loop
        self.fifos = {}
        self.queue = Queue(loop=self.loop)
        self.sleep_delay = .2

        self.context.create_task(self.process_queue())

    def process_queue(self):
        while True:
            channel, message = yield from self.queue.get()
            self.context.privmsg(channel, message)
            yield from asyncio.sleep(self.context.config.min_delay,
                                     loop=self.loop)

    def watch_fd(self, channel, fd, *args):
        while True:
            data = True
            msgs = []
            while data:
                try:
                    data = fd.readline()
                except (IOError, OSError):
                    break
                if data:
                    if not self.send_blank_line and not data.strip():
                        continue
                    msgs.append(data)
            if msgs:
                for msg in msgs:
                    self.queue.put_nowait((channel, msg))
            yield from irc3.asyncio.sleep(self.sleep_delay, loop=self.loop)

    def create_fifo(self, channel):
        path = os.path.join(self.runpath, channel.strip('#&+'))
        if not os.path.exists(path):
            os.mkfifo(path)
        fileno = os.open(path, os.O_RDONLY | os.O_NDELAY)
        fd = os.fdopen(fileno)
        meth = partial(self.watch_fd, channel, fd)
        self.loop.call_soon(meth)
        self.log.debug("%s's fifo is %r", channel, fd)
        return meth

    @irc3.event(irc3.rfc.JOIN)
    def join(self, mask=None, channel=None, **kwargs):
        if mask.nick == self.context.nick:
            if channel not in self.fifos:
                self.fifos[channel] = self.create_fifo(channel)
