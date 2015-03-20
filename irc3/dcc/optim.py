# -*- coding: utf-8 -*-
from irc3.dcc.client import DCCSend as DCCSendBase
try:
    from os import sendfile
except ImportError:
    from sendfile import sendfile


class DCCSend(DCCSendBase):
    """DCC SEND implementation"""

    _sendfile = sendfile

    def send_chunk(self):
        sent = self._sendfile(self.socket.fileno(), self.fd_fileno,
                              self.offset, self.block_size)
        return sent
