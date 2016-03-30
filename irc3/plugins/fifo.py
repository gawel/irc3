# -*- coding: utf-8 -*-
import os
import irc3
import logging
from functools import partial
from irc3.compat import Queue


@irc3.plugin
class Fifo(object):

    def __init__(self, context):
        self.log = logging.getLogger(__name__)
        self.context = context
        self.config = self.context.config[__name__]
        self.send_blank_line = self.config.get('send_blank_line', True)

        self.runpath = self.config['runpath']
        if not os.path.exists(self.runpath):
            os.makedirs(self.runpath)

        self.loop = self.context.loop
        self.fifos = {}
        self.queue = Queue()
        self.time = int(self.loop.time())
        self.sleep_delay = .2

        self.process_queue()

    def process_queue(self, f=None):
        if f is not None:
            if f.result():
                # we have a (channel, message)
                time = int(self.loop.time())
                ttime = self.time + .5
                if time < ttime:
                    self.time = ttime
                else:
                    self.time = time
                self.loop.call_at(self.time, self.context.privmsg, *f.result())
        task = self.context.create_task(self.queue.get())
        task.add_done_callback(self.process_queue)

    def watch_fd(self, channel, fd, *args):
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
                self.context.create_task(self.queue.put((channel, msg)))
        task = self.context.create_task(irc3.asyncio.sleep(self.sleep_delay))
        task.add_done_callback(self.fifos[channel])

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
