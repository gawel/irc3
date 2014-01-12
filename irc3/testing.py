# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from unittest import TestCase
import irc3
from irc3.compat import PY3
import os

try:
    from unittest import mock
except ImportError:
    import mock

MagicMock = mock.MagicMock
patch = mock.patch
call = mock.call

passwd_ini = """
[irc.freenode.net]
irc3=password

[twitter]
key=key
secret=secret
token=token
token_secret=token_secret
"""


def call_later(i, func, *args):
    if func.__name__ in dir(IrcBot):
        return func(*args)


def call_soon(func, *args):
    return func(*args)


class IrcBot(irc3.IrcBot):

    def __init__(self, **config):
        self.check_required()
        loop = MagicMock()
        loop.call_later = call_later
        loop.call_soon = call_soon
        loop.time = MagicMock()
        loop.time.return_value = 10
        config.update(testing=True, async=False, level=1000,
                      loop=loop)
        super(IrcBot, self).__init__(**config)
        self.protocol = irc3.IrcConnection()
        self.protocol.factory = self
        self.protocol.transport = MagicMock()
        self.protocol.write = MagicMock()

    def check_required(self):
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
            for line in self.sent:
                if PY3:
                    print(line)
                else:
                    print(line.encode('utf8'))

    @property
    def sent(self):
        values = [tuple(c)[0][0] for c in self.protocol.write.call_args_list]
        self.protocol.write.reset_mock()
        if not PY3:
            return [v.encode('utf8') for v in values]
        return values


class BotTestCase(TestCase):

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
        else:
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

    def patch_requests(self, **kwargs):
        self.patcher = patch('requests.Session.request')
        self.addCleanup(self.patcher.stop)
        request = self.patcher.start()

        filename = kwargs.pop('filename', None)
        if filename:
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
        patcher = patch('asyncio.Task')
        self.Task = patcher.start()
        self.addCleanup(patcher.stop)
        patcher = patch('asyncio.get_event_loop')
        patcher.start()
        self.addCleanup(patcher.stop)
