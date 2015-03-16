# -*- coding: utf-8 -*-
from irc3.dcc.client import DCCSend as DCCSendBase
from sendfile import sendfile


class DCCSend(DCCSendBase):

    def send_chunk(self):
        with open(self.filepath, 'rb') as fd:
            sent = sendfile(self.socket.fileno(), fd.fileno(),
                            self.offset, self.block_size)
        return sent
