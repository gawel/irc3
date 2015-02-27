# -*- coding: utf-8 -*-
from irc3.testing import BotTestCase
import tempfile
import shutil
import sys
import os

plugin = '''
from irc3.plugins.cron import cron
from irc3.plugins.command import command
import irc3

class P(object):

    requires = [
        'irc3.plugins.cron',
        'irc3.plugins.command',
    ]

    def __init__(self, context, old=None):
        self.context = context
        self.old = old

    @cron('* * * * *')
    def cron(self):
        pass

    @irc3.event(irc3.rfc.PRIVMSG)
    def event(self, **kwargs):
        pass

    @irc3.extend
    def extend(self, **kwargs):
        return self.old

    @command()
    def cmd(self, *args, **kwargs):
        """
        %%cmd
        """
        yield str(id(self))

    @classmethod
    def reload(cls, old):
        new = cls(old.context, old=old)
        return new

'''


class TestReload(BotTestCase):

    def test_reload(self):
        # add test plugin to pythonpath
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        sys.path.append(tmp)
        with open(os.path.join(tmp, 'p.py'), 'w') as fd:
            fd.write(plugin)

        bot = self.callFTU()
        bot.include('p')
        p = bot.get_plugin('p.P')
        assert p.extend() is None
        assert bot.extend() is None
        crons = bot.get_plugin('irc3.plugins.cron.Crons')
        assert len(crons) == 1
        assert len(bot.registry.events['in']) == 6
        bot.dispatch(':adm!user@host PRIVMSG #chan :!cmd')
        self.assertSent(['PRIVMSG #chan :%s' % id(p)])

        # modify test plugin
        with open(os.path.join(tmp, 'p.py'), 'a') as fd:
            fd.write('x = 1')
        bot.reload()

        # assume it's reloaded
        np = bot.get_plugin('p.P')
        assert np is not p
        assert np.extend() is p
        assert bot.extend() is p
        assert crons == bot.get_plugin('irc3.plugins.cron.Crons')
        assert len(crons) == 1
        assert len(bot.registry.events['in']) == 6
        bot.dispatch(':adm!user@host PRIVMSG #chan :!cmd')
        self.assertSent(['PRIVMSG #chan :%s' % id(np)])
