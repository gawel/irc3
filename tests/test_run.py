# -*- coding: utf-8 -*-
from docopt import DocoptExit
from irc3 import testing
import tempfile
import shutil
import irc3d
import irc3
import os


class TestRun(testing.BotTestCase):

    def setUp(self):
        self.patch_asyncio()
        self.addCleanup(setattr, irc3.IrcBot,
                        'logging_config',
                        irc3.config.LOGGING)
        self.wd = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.wd)
        self.wd = os.path.join(self.wd, 'logs')

    def callFTU(self, *args):
        return irc3.run(args)

    def test_args_error(self):
        self.assertRaises(DocoptExit, self.callFTU, '-x')

    def test_logdir(self):
        bot = self.callFTU('-dr', 'tests/test.ini', '--logdir=' + self.wd)
        self.assertEqual(
            bot.logging_config['handlers']['console']['formatter'], 'file')
        self.assertTrue(self.Task.called)


class TestServerRun(testing.ServerTestCase):

    def setUp(self):
        self.patch_asyncio()
        self.addCleanup(setattr, irc3d.IrcServer,
                        'logging_config',
                        irc3.config.LOGGING)
        self.wd = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.wd)
        self.wd = os.path.join(self.wd, 'logs')

    def callFTU(self, *args):
        return irc3d.run(args)

    def test_args_error(self):
        self.assertRaises(DocoptExit, self.callFTU, '-x')

    def test_logdir(self):
        bot = self.callFTU('-dr', 'tests/test.ini', '--logdir=' + self.wd)
        self.assertEqual(
            bot.logging_config['handlers']['console']['formatter'], 'file')
        self.assertTrue(self.Task.called)
