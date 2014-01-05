# -*- coding: utf-8 -*-
from irc3.testing import BotTestCase
from docopt import DocoptExit
import tempfile
import shutil
import irc3
import os


class TestRun(BotTestCase):

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
        bot = self.callFTU('-dr', 'examples/bot.ini', '--logdir=' + self.wd)
        self.assertEqual(
            bot.logging_config['handlers']['console']['formatter'], 'file')
        self.assertTrue(self.Task.called)
