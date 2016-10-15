# -*- coding: utf-8 -*-
import os
import irc3
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
    >>> print(sorted(os.listdir('/tmp/run/irc3')))
    [':raw', 'channel']

You'll be able to print stuff to a channel from a shell::

    $ cat /etc/passwd > /tmp/run/irc3/channel

You can also send raw irc commands using the ``:raw`` file::

    $ echo JOIN \#achannel > /tmp/run/irc3/:raw
'''


@irc3.plugin
class Fifo:

    BLOCK_SIZE = 1024
    MAX_BUFFER_SIZE = 800

    def __init__(self, context):
        self.context = context
        self.config = self.context.config[__name__]
        self.send_blank_line = self.config.get('send_blank_line', True)

        self.runpath = self.config.get('runpath', '/run/irc3')
        if not os.path.exists(self.runpath):
            os.makedirs(self.runpath)

        self.loop = self.context.loop
        self.fifos = {}
        self.buffers = {}
        self.create_fifo(None)

    @classmethod
    def read_fd(cls, fd):  # pragma: no cover
        # this required for python < 3.5
        # for more info see https://www.python.org/dev/peps/pep-0475/
        while True:
            try:
                return os.read(fd, cls.BLOCK_SIZE)
            except InterruptedError:
                continue
            except BlockingIOError:
                return b""

    def handle_line(self, line, channel):
        if not line:
            return

        line = line.decode("utf8")
        if not self.send_blank_line and not line.strip():
            return

        if channel is None:
            self.context.send_line(line)
        else:
            self.context.privmsg(channel, line)

    def data_received(self, data, channel):
        if not data:
            return

        prev = self.buffers.get(channel, b"")
        lines = (prev + data).splitlines(True)
        last = lines[-1]
        for line in lines[:-1]:
            line = line.rstrip(b'\r\n')
            self.handle_line(line, channel)

        if last.endswith(b'\n'):
            line = last.rstrip(b'\r\n')
            self.handle_line(line, channel)
            self.buffers[channel] = b""
            return

        if len(last) > self.MAX_BUFFER_SIZE:
            self.handle_line(last, channel)
            self.buffers[channel] = b""
        else:
            self.buffers[channel] = last

    def watch_fd(self, fd, channel):
        reading = True

        while reading:
            data = self.read_fd(fd)
            reading = len(data) == self.BLOCK_SIZE
            self.data_received(data, channel)

    def create_fifo(self, channel):
        if channel is None:
            path = os.path.join(self.runpath, ':raw')
        else:
            path = os.path.join(self.runpath, channel.strip('#&+'))
        if not os.path.exists(path):
            os.mkfifo(path)
        fd = os.open(path, os.O_RDWR | os.O_NONBLOCK)
        self.loop.add_reader(fd, self.watch_fd, fd, channel)
        self.context.log.debug("%s's fifo is %s %r",
                               channel or ':raw', path, fd)
        return fd

    @irc3.event(irc3.rfc.JOIN)
    def join(self, mask=None, channel=None, **kwargs):
        if mask.nick == self.context.nick:
            if channel not in self.fifos:
                self.fifos[channel] = self.create_fifo(channel)
