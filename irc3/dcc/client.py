# -*- coding: utf-8 -*-
import struct
from functools import partial
from irc3.compat import asyncio


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
        self.started.set_result(True)

    def connection_lost(self, exc):
        self.close(exc)

    def close(self, result=None):
        if self.idle_handle is not None:
            self.idle_handle.cancel()
        if self.transport:
            self.transport.close()
        info = self.manager.connections[self.type]
        if self.port in info['masks'][self.mask]:
            info['total'] -= 1
            del info['masks'][self.mask][self.port]
        if not self.closed.done():
            self.closed.set_result(result)

    def data_received(self, data):
        self.set_timeout()
        self.dispatch(data)

    def set_timeout(self):
        if self.idle_handle is not None:
            self.idle_handle.cancel()
        if self.idle_timeout:
            self.idle_handle = self.loop.call_later(
                self.idle_timeout, self.idle_timeout_reached)

    def idle_timeout_reached(self):
        if self.type == 'chat':
            msg = "Your idle is too high. Closing connection."
            self.send_line(msg)
        self.close()


class DCCChat(DCCBase):

    type = 'chat'
    ctcp = 'DCC CHAT chat {0.ip} {0.port}'

    def connection_made(self, transport):
        super(DCCChat, self).connection_made(transport)
        self.set_timeout()

    def dispatch(self, data):
        data = data.strip(' \r\n')
        self.send(*data.split('\n'))

    def send_line(self, message):
        if not isinstance(message, bytes):
            message = message.encode('utf-8')
        self.transport.write(message + b'\r\n')

    def send(self, *messages):
        for message in messages:
            self.send_line(message)

    def action(self, message):
        if not isinstance(message, bytes):
            message = message.encode('utf-8')
        message = b'\x01ACTION ' + message + b'\x01'
        self.send_line(message)

    def actions(self, *messages):
        for message in messages:
            self.action(message)


class DCCGet(DCCBase):
    type = 'get'
    ctcp = None

    def connection_made(self, transport):
        super(DCCGet, self).connection_made(transport)
        if self.resume:
            self.bytes_received = self.offset
        else:
            self.bytes_received = 0

    def dispatch(self, data):
        with open(self.filepath, 'ab') as fd:
            fd.write(data)
        self.bytes_received += len(data)
        self.transport.write(struct.pack('!I', self.bytes_received))


class DCCSend(DCCBase):

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
        self.loop.remove_writer(socket)
        self.loop.add_writer(socket, self.next_chunk)

    def send_chunk(self):
        with open(self.filepath, 'rb') as fd:
            fd.seek(self.offset)
            sent = self.socket.send(fd.read(self.block_size))
        return sent

    def next_chunk(self):
        sent = self.send_chunk()
        if sent != 0:
            self.offset += sent
            cb = partial(self.loop.add_writer, self.socket, self.next_chunk)
            if self.delay is not None:
                self.loop.call_later(self.delay, cb)
            else:
                cb()
        else:
            self.loop.remove_writer(self.socket)

    def dispatch(self, data):
        bytes_received = (
            struct.unpack('!I', data[i:i+4])[0]
            for i in range(0, len(data), 4))
        for recv in bytes_received:
            if recv == self.filesize:
                self.transport.close()
