# -*- coding: utf-8 -*-
import os
import string
import asyncio
import tempfile
import irc3
from irc3.plugins.command import command


@irc3.plugin
class DCC(object):

    filename = os.path.join(tempfile.gettempdir(), 'to_send')

    def __init__(self, bot):
        self.bot = bot
        if not os.path.isfile(self.filename):
            # create a file to send
            with open(self.filename, 'wb') as fd:
                for i in range(64 * 2048):
                    fd.write(string.ascii_letters.encode('utf8'))

    @command
    @asyncio.coroutine
    def send(self, mask, target, args):
        """ DCC SEND command

            %%send
        """
        conn = yield from self.bot.dcc_send(mask, self.filename)
        self.bot.log.debug('%s ready', conn)
