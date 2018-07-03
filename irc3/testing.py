# -*- coding: utf-8 -*-
from unittest import TestCase
import irc3
import irc3d
from irc3.compat import asyncio
import tempfile
import time
import os

try:
    from unittest import mock
except ImportError:  # pragma: no cover
    import mock

MagicMock = mock.MagicMock
patch = mock.patch
call = mock.call
PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

passwd_ini = """
[irc.freenode.net]
irc3=password

[twitter]
key=key
secret=secret
token=token
token_secret=token_secret
"""


def ini2config(data, type='bot'):
    data = data.encode('utf8')
    with tempfile.NamedTemporaryFile(prefix='irc3-') as fd:
        fd.write(data)
        fd.flush()
        data = irc3.utils.parse_config(type, fd.name)
    return data


def call_later(i, func, *args):
    if func.__name__ in dir(IrcBot):
        func(*args)
    return asyncio.Handle(func, args, asyncio.get_event_loop())


def call_soon(func, *args):
    func(*args)
    return asyncio.Handle(func, args,  asyncio.get_event_loop())


class IrcBot(irc3.IrcBot):

    def __init__(self, **config):
        self.check_required()
        if 'loop' not in config:
            loop = asyncio.new_event_loop()
            loop = mock.create_autospec(loop, spec_set=True)
            loop.call_later = call_later
            loop.call_soon = call_soon
            loop.time.return_value = 10
            config.update(testing=True, asynchronous=False, level=1000,
                          loop=loop)
        else:
            config.update(testing=True, level=1000)
        super(IrcBot, self).__init__(**config)
        self.protocol = irc3.IrcConnection()
        self.protocol.closed = False
        self.protocol.factory = self
        self.protocol.transport = MagicMock()
        self.protocol.write = MagicMock()

    def check_required(self):  # pragma: no cover
        dirname = os.path.expanduser('~/.irc3')
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        filename = os.path.expanduser('~/.irc3/passwd.ini')
        if not os.path.isfile(filename):
            with open(filename, 'w') as fd:
                fd.write(passwd_ini)

    def test(self, data, show=True):
        self.dispatch(data)
        if show:
            for line in self.sent:  # pragma: no cover
                print(line)

    @property
    def sent(self):
        values = [tuple(c)[0][0] for c in self.protocol.write.call_args_list]
        self.protocol.write.reset_mock()
        return values


class IrcTestCase(TestCase):

    project_path = PROJECT_PATH

    def patch_requests(self, **kwargs):
        self.patcher = patch('requests.Session.request')
        self.addCleanup(self.patcher.stop)
        request = self.patcher.start()

        filename = kwargs.pop('filename', None)
        if filename:
            filename = os.path.join(self.project_path, filename)
            with open(filename, 'rb') as feed:
                content = feed.read()
            for k, v in kwargs.items():
                content = content.replace(k.encode('ascii'), v.encode('ascii'))
            kwargs['content'] = content
            kwargs['text'] = content.decode('utf8')
        kwargs.setdefault('status_code', 200)
        resp = MagicMock(**kwargs)
        for k, v in kwargs.items():
            if k in ('json',):
                setattr(resp, k, MagicMock(return_value=v))
        request.return_value = resp
        return request

    def patch_asyncio(self):
        patcher = patch('irc3.compat.asyncio.Task')
        self.Task = patcher.start()
        self.addCleanup(patcher.stop)
        patcher = patch('irc3.compat.asyncio.get_event_loop')
        patcher.start()
        self.addCleanup(patcher.stop)


class BotTestCase(IrcTestCase):

    config = {'nick': 'nono'}

    def callFTU(self, **config):
        config = dict(self.config, **config)
        bot = IrcBot(**config)
        self.bot = bot
        return bot

    def assertSent(self, lines):
        if not lines:
            self.assertNothingSent()
            return
        if not self.bot.loop.called:
            self.bot.protocol.write.assert_has_calls(
                [call(l) for l in lines])
        else:  # pragma: no cover
            self.bot.loop.call_later.assert_has_calls(
                [call(l) for l in lines])
        self.reset_mock()

    def assertNothingSent(self):
        self.assertFalse(self.bot.protocol.write.called)
        self.assertFalse(self.bot.loop.called)
        self.reset_mock()

    def reset_mock(self):
        self.bot.protocol.write.reset_mock()
        self.bot.loop.reset_mock()


class IrcClient(irc3d.IrcClient):

    def __init__(self):
        self.sent = []

    def dispatch(self, data):
        self.data['data_received'] = time.time()
        return self.factory.dispatch(data, client=self)

    def write(self, data):
        super(IrcClient, self).write(data)
        self.sent.extend(data.split('\r\n'))

    def reset(self, data=False):
        self.sent = []
        if data:  # pragma: no cover
            self.data = []


class IrcServer(irc3d.IrcServer):

    def __init__(self, **config):
        loop = MagicMock()
        loop.call_later = call_later
        loop.call_soon = call_soon
        loop.time = MagicMock()
        loop.time.return_value = 10
        config.update(testing=True, asynchronous=False, level=1000,
                      loop=loop)
        super(IrcServer, self).__init__(**config)
        print(self.clients)

    def add_clients(self, amount=2):
        for i in range(1, amount + 1):
            client = IrcClient()
            client.factory = self
            transport = MagicMock()
            transport.get_extra_info.return_value = ('127.0.0.1', i)
            client.connection_made(transport)
            nick = 'client%s' % i
            client.data.update(nick=nick)
            client.dispatch(
                "USER u{0} 127.0.0.1 127.0.0.1 :I'm {0}".format(nick))
            setattr(self, nick, client)


class ServerTestCase(IrcTestCase):

    config = {'servername': 'irc.com',
              'includes': ['irc3d.plugins.core']}

    def callFTU(self, clients=2, **config):
        config = dict(self.config, **config)
        server = IrcServer(**config)
        server.add_clients(amount=clients)
        self.server = server
        return server

    def assertSent(self, client, data, origin=None):
        if origin:
            data = data.format(**origin.data)
        self.assertIn(data, client.sent)

    def assertNotSent(self, client, data, origin=None):
        if origin:
            data = data.format(**origin.data)
        self.assertNotIn(data, client.sent)
