# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import struct
from collections import deque
from functools import partial
from irc3.compat import asyncio
from irc3.compat import text_type


class DCCBase(asyncio.Protocol):

    idle_handle = None
    idle_timeout = None
    fd = None

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.ready = asyncio.Future(loop=self.loop)
        self.started = asyncio.Future(loop=self.loop)
        self.closed = asyncio.Future(loop=self.loop)
        self.timeout_handle = None

    def factory(self):
        return self

    def connection_made(self, transport):
        self.transport = transport
        self.started.set_result(self)

    def connection_lost(self, exc):
        self.close(exc)

    def close(self, result=None):
        if self.idle_handle is not None:
            self.idle_handle.cancel()
        if self.transport:
            self.transport.close()
        info = self.bot.dcc.connections[self.type]
        if self.port in info['masks'][self.mask]:
            info['total'] -= 1
            del info['masks'][self.mask][self.port]
        if not self.closed.done():
            self.closed.set_result(result)
        self.bot.log.debug('%s closed', self)

    def set_timeout(self):
        if self.idle_handle is not None:
            self.idle_handle.cancel()
        if self.idle_timeout:
            self.idle_handle = self.loop.call_later(
                self.idle_timeout, self.idle_timeout_reached)

    def idle_timeout_reached(self, *args):
        if self.type == 'chat':
            msg = "Your idle is too high. Closing connection."
            self.send_line(msg)
        self.close()

    def __str__(self):
        return '%s with %s' % (self.__class__.__name__, self.mask)

    def __repr__(self):
        return '<%s with %s>' % (self.__class__.__name__, self.mask)


class DCCChat(DCCBase):
    """DCC CHAT implementation"""

    type = 'chat'
    ctcp = 'DCC CHAT chat {0.ip} {0.port}'

    def connection_made(self, transport):
        super(DCCChat, self).connection_made(transport)
        self.encoding = getattr(self.bot, 'encoding', 'ascii')
        self.set_timeout()
        self.queue = deque()

    def decode(self, data):
        """Decode data with bot's encoding"""
        return data.decode(self.encoding, 'ignore')

    def data_received(self, data):
        """data received"""
        self.set_timeout()
        data = self.decode(data)
        if self.queue:
            data = self.queue.popleft() + data
        lines = data.replace('\r', '').split('\n')
        self.queue.append(lines.pop(-1))
        for line in lines:
            self.bot.dispatch(line, iotype='dcc_in', client=self)

    def encode(self, data):
        """Encode data with bot's encoding"""
        if isinstance(data, text_type):
            data = data.encode(self.encoding)
        return data

    def write(self, data):
        if data is not None:
            data = self.encode(data)
            if not data.endswith(b'\r\n'):
                data = data + b'\r\n'
            self.transport.write(data)

    def send_line(self, message):
        self.write(message)
        self.bot.dispatch(message, iotype='dcc_out', client=self)

    def send(self, *messages):
        for message in messages:
            self.send_line(message)

    def action(self, message):
        message = '\x01ACTION ' + message + '\x01'
        self.send_line(message)

    def actions(self, *messages):
        for message in messages:
            self.action(message)


class DCCGet(DCCBase):
    """DCC GET implementation"""
    type = 'get'
    ctcp = None

    def connection_made(self, transport):
        super(DCCGet, self).connection_made(transport)
        if self.resume:
            self.bytes_received = self.offset
        else:
            self.bytes_received = 0
        self.fd = open(self.filepath, 'ab')

    def data_received(self, data):
        self.set_timeout()
        self.fd.write(data)
        self.bytes_received += len(data)
        self.transport.write(struct.pack('!I', self.bytes_received))

    def close(self, *args, **kwargs):
        if self.fd:
            self.fd.close()
            self.fd = None
        super(DCCGet, self).close(*args, **kwargs)


class DCCSend(DCCBase):
    """DCC SEND implementation"""

    type = 'send'
    ctcp = 'DCC SEND {0.filename_safe} {0.ip} {0.port} {0.filesize}'
    block_size = 1024 * 64
    limit_rate = None
    filepath = None

    def connection_made(self, transport):
        super(DCCSend, self).connection_made(transport)
        self.delay = 1. / (self.limit_rate / 64.) if self.limit_rate else None
        socket = self.transport.get_extra_info('socket')
        self.socket = socket
        self.sendfile = getattr(self.socket, 'sendfile', None)
        if self.sendfile:
            self.socket.setblocking(1)
        self.fd = open(self.filepath, 'rb')
        self.fd_fileno = self.fd.fileno()
        self.loop.remove_writer(socket)
        self.loop.add_writer(socket, self.next_chunk)

    def write(self, *args):  # pragma: no cover
        raise NotImplementedError('write is not available during DCCSend')

    def send_chunk(self):
        if self.sendfile:
            sent = self.sendfile(self.fd, self.offset, self.block_size)
        else:
            self.fd.seek(self.offset)
            sent = self.socket.send(self.fd.read(self.block_size))
        return sent

    def next_chunk(self):
        try:
            sent = self.send_chunk()
        except Exception as e:  # pragma: no cover
            self.bot.log.exception(e)
            self.fd.close()
            sent = 0
        if sent != 0:
            self.offset += sent
            cb = partial(self.loop.add_writer, self.socket, self.next_chunk)
            if self.delay is not None:
                self.loop.call_later(self.delay, cb)
            else:
                cb()
        else:
            self.loop.remove_writer(self.socket)

    def data_received(self, data):
        self.set_timeout()
        bytes_received = (
            struct.unpack('!I', data[i:i+4])[0]
            for i in range(0, len(data), 4))
        for recv in bytes_received:
            if recv == self.filesize:
                self.transport.close()

    def close(self, *args, **kwargs):
        if self.fd:
            self.fd.close()
            self.fd = None
        super(DCCSend, self).close(*args, **kwargs)
