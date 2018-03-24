# -*- coding: utf-8 -*-
from irc3.plugins.command import command
from irc3.compat import Queue
import irc3


@irc3.plugin
class AsyncCommands(object):
    """Async commands example. This is what it's look like on irc::

        <gawel> !get
        <gawel> !put item
        <irc3> items added to queue
        <irc3> item
    """

    def __init__(self, bot):
        self.bot = bot
        self.queue = Queue()

    @command
    def put(self, mask, target, args):
        """Put items in queue

            %%put <words>...
        """
        for w in args['<words>']:
            self.queue.put_nowait(w)
        yield 'items added to queue'

    @command
    async def get(self, mask, target, args):
        """Async get items from the queue

            %%get
        """
        messages = []
        message = await self.queue.get()
        messages.append(message)
        while not self.queue.empty():
            message = await self.queue.get()
            messages.append(message)
        return messages
