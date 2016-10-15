# -*- coding: utf-8 -*-
from irc3.testing import BotTestCase
from irc3.compat import asyncio
from irc3.dcc.client import DCCSend
from irc3.dcc.optim import DCCSend as DCCSendOptim
from irc3.plugins.dcc import dcc_command
from irc3 import dcc_event
from irc3 import utils
import tempfile
import pytest
import shutil
import os


log = {'in': [], 'out': []}


def get_extra_info(*args):
    return ('127.0.0.1', 4567)


@dcc_event('(?P<data>.*)')
def log_in(bot, client=None, data=None):
    log['in'].append((client, data))


@dcc_event('(?P<data>.*)', iotype='out')
def log_out(bot, client=None, data=None):
    log['out'].append((client, data))


@dcc_command
def syn(bot, mask, client, args):
    """Ok

        %%syn
    """
    client.send_line('ack')


def chat_ready(client):
    client = client.result()
    client.actions(client.mask)
    client.send('\x01ACTION syn\x01')
    client.send('\x01ACTION help\x01')
    client.loop.call_later(.1, client.idle_timeout_reached)


@pytest.mark.usefixtures('cls_event_loop')
class TestChat(BotTestCase):

    config = dict(includes=['irc3.plugins.dcc'],
                  dcc={'ip': '127.0.0.1'})
    mask = utils.IrcString('gawel@gawel!bearstech.com')
    dmask = utils.IrcString('gawel@gawel!127.0.0.1')

    def callDCCFTU(self, *args, **kwargs):
        self.bot = self.callFTU()
        self.bot.protocol.transport.get_extra_info = get_extra_info
        self.bot.dispatch(':%s PRIVMSG irc3 :!chat' % self.mask)
        self.future = asyncio.Future(loop=self.loop)
        self.loop.call_later(.1, self.created)

    def created(self):
        servers = self.bot.dcc.connections['chat']['masks'][self.mask]
        self.server = list(servers.values())[0]
        print(self.server)
        self.client = self.bot.dcc.create(
            'chat', self.dmask,
            host='127.0.0.1', port=self.server.port)
        self.client.ready.add_done_callback(chat_ready)
        self.client.closed.add_done_callback(self.future.set_result)

    def test_create(self):
        self.callDCCFTU()
        self.bot.include('irc3.plugins.dcc')
        self.bot.include(__name__)
        self.loop.run_until_complete(self.future)
        proto = self.client
        assert proto.transport is not None
        info = self.bot.dcc.connections['chat']['masks']['gawel']
        assert proto not in info.values()
        assert proto.started.result() is proto
        assert proto.closed.done()

        # the timeout message is sent or not regarding python version.
        # we tolerate both
        assert len(log['in']) in (5, 6)
        assert len(log['out']) == 6


@pytest.mark.usefixtures('cls_event_loop')
class DCCTestCase(BotTestCase):

    dmask = utils.IrcString('gawel@gawel!127.0.0.1')

    def callDCCFTU(self, *args, **kwargs):
        bot = self.callFTU()
        self.future = asyncio.Future(loop=self.loop)
        bot.protocol.transport.get_extra_info = get_extra_info
        self.manager = manager = bot.dcc
        self.server = manager.create(*args, **kwargs)
        self.server.ready.add_done_callback(self.created)

    def createFiles(self):
        self.wd = tempfile.mkdtemp(prefix='irc3dcc')
        self.addCleanup(shutil.rmtree, self.wd)
        self.dst = os.path.join(self.wd, 'dst')
        self.src = os.path.join(self.wd, 'src')
        with open(self.src, 'wb') as fd:
            fd.write(('start%ssend' % ('---' * (1024 * 1024))).encode('ascii'))

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
            'get', utils.IrcString('gawel!gawel@host'),
            host='127.0.0.1', port=self.server.port,
            idle_timeout=10, filepath=self.dst)
        self.client.closed.add_done_callback(self.future.set_result)

    def test_create(self):
        self.createFiles()
        self.callDCCFTU(self.send_class, self.dmask, filepath=self.src)
        self.loop.run_until_complete(self.future)
        proto = self.client
        assert proto.transport is not None
        info = self.manager.connections['get']['masks'][self.dmask]
        assert proto not in info.values()
        assert proto.started.result() is proto
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
            'get', self.dmask,
            host='127.0.0.1', port=self.server.port,
            idle_timeout=10, filepath=self.dst)
        self.client.resume = True
        self.manager.resume(self.dmask, self.server.filename_safe,
                            self.server.port, self.client.offset)
        self.client.closed.add_done_callback(self.future.set_result)

    def test_create(self):
        self.createFiles()
        self.callDCCFTU(self.send_class, self.dmask, filepath=self.src)
        self.loop.run_until_complete(self.future)
        proto = self.client
        assert proto.transport is not None
        info = self.manager.connections['get']['masks'][self.dmask]
        assert proto not in info.values()
        assert proto.started.result() is proto
        assert proto.closed.done()
        self.assertFileSent()


class TestResumeOptim(TestResume):

    send_class = DCCSendOptim


class TestSendWithLimit(DCCTestCase):

    send_class = DCCSend

    def created(self, f):
        self.client = self.manager.create(
            'get', self.dmask,
            host='127.0.0.1', port=self.server.port,
            idle_timeout=10, filepath=self.dst)
        self.client.closed.add_done_callback(self.future.set_result)

    def test_create(self):
        self.createFiles()
        self.callDCCFTU(self.send_class, self.dmask,
                        filepath=self.src, limit_rate=64)
        self.loop.run_until_complete(self.future)
        proto = self.client
        assert proto.transport is not None
        info = self.manager.connections['get']['masks'][self.dmask]
        assert proto not in info.values()
        assert proto.started.result() is proto
        assert proto.closed.done()
        self.assertFileSent()


class TestSendWithLimitOptim(TestSendWithLimit):

    send_class = DCCSendOptim
