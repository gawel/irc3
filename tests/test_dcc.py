# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from irc3.testing import BotTestCase
from irc3.compat import asyncio
from irc3.dcc.client import DCCSend
from irc3.dcc.optim import DCCSend as DCCSendOptim
from irc3 import dcc
import tempfile
import shutil
import os


def get_extra_info(*args):
    return ('127.0.0.1', 4567)


class DCCTestCase(BotTestCase):

    loop = asyncio.new_event_loop()
    config = dict(loop=loop)

    def callDCCFTU(self, *args, **kwargs):
        bot = self.callFTU()
        self.future = asyncio.Future(loop=self.loop)
        bot.protocol.transport.get_extra_info = get_extra_info
        self.manager = manager = bot.dcc_manager
        manager.connection_made()
        self.server = manager.create(*args, **kwargs)
        self.server.ready.add_done_callback(self.created)

    def createFiles(self):
        self.wd = tempfile.mkdtemp(prefix='irc3dcc')
        self.addCleanup(shutil.rmtree, self.wd)
        self.dst = os.path.join(self.wd, 'dst')
        self.src = os.path.join(self.wd, 'src')
        with open(self.src, 'wb') as fd:
            fd.write('start%send' % ('---' * (1024 * 1024)))

    def assertFileSent(self):
        getsize = os.path.getsize
        assert getsize(self.dst), getsize(self.src)
        assert getsize(self.dst), getsize(self.src)
        with open(self.src, 'rb') as fd:
            src = fd.read()
        with open(self.dst, 'rb') as fd:
            dest = fd.read()
        assert src == dest


class TestSend(DCCTestCase):

    send_class = DCCSend

    def created(self, f):
        self.client = self.manager.create(
            'get', 'gawel',
            host='127.0.0.1', port=self.server.port,
            idle_timeout=10, filepath=self.dst)
        self.client.closed.add_done_callback(self.future.set_result)

    def test_create(self):
        self.createFiles()
        self.callDCCFTU(self.send_class, 'gawel', filepath=self.src)
        self.loop.run_until_complete(self.future)
        proto = self.client
        assert proto.transport is not None
        info = self.manager.connections['get']['masks']['gawel']
        assert proto not in info.values()
        assert proto.started.result() is True
        assert proto.closed.done()
        self.assertFileSent()


class TestSendOptim(TestSend):

    send_class = DCCSendOptim


class TestResume(DCCTestCase):

    send_class = DCCSend

    def created(self, f):
        with open(self.dst, 'wb') as fd:
            with open(self.src, 'rb') as fdd:
                fd.write(fdd.read(1345))
        self.client = self.manager.create(
            'get', 'gawel',
            host='127.0.0.1', port=self.server.port,
            idle_timeout=10, filepath=self.dst)
        self.client.resume = True
        self.manager.resume('gawel', self.server.filename_safe,
                            self.server.port, self.client.offset)
        self.client.closed.add_done_callback(self.future.set_result)

    def test_create(self):
        self.createFiles()
        self.callDCCFTU(self.send_class, 'gawel', filepath=self.src)
        self.loop.run_until_complete(self.future)
        proto = self.client
        assert proto.transport is not None
        info = self.manager.connections['get']['masks']['gawel']
        assert proto not in info.values()
        assert proto.started.result() is True
        assert proto.closed.done()
        self.assertFileSent()


class TestResumeOptim(TestResume):

    send_class = DCCSendOptim


class TestSendWithLimit(DCCTestCase):

    send_class = DCCSend

    def created(self, f):
        self.client = self.manager.create(
            'get', 'gawel',
            host='127.0.0.1', port=self.server.port,
            idle_timeout=10, filepath=self.dst)
        self.client.closed.add_done_callback(self.future.set_result)

    def test_create(self):
        self.createFiles()
        self.callDCCFTU(self.send_class, 'gawel',
                        filepath=self.src, limit_rate=64)
        self.loop.run_until_complete(self.future)
        proto = self.client
        assert proto.transport is not None
        info = self.manager.connections['get']['masks']['gawel']
        assert proto not in info.values()
        assert proto.started.result() is True
        assert proto.closed.done()
        self.assertFileSent()


class TestSendWithLimitOptim(TestSendWithLimit):

    send_class = DCCSendOptim


class Chat(dcc.DCCChat):

    def connection_made(self, transport):
        super(Chat, self).connection_made(transport)
        self.send('Yo!')
        self.actions('OUPS')
        self.loop.call_later(.001, self.idle_timeout_reached)


class TestChat(DCCTestCase):

    def created(self, f):
        self.client = self.manager.create(
            Chat, 'gawel', host='127.0.0.1', port=self.server.port)
        self.client.closed.add_done_callback(self.future.set_result)

    def test_create(self):
        self.callDCCFTU(Chat, 'gawel')
        self.loop.run_until_complete(self.future)
        proto = self.client
        assert proto.transport is not None
        info = self.manager.connections['chat']['masks']['gawel']
        assert proto not in info.values()
        assert proto.started.result() is True
        assert proto.closed.done()
