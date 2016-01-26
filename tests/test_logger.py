# -*- coding: utf-8 -*-
from irc3.testing import BotTestCase
import tempfile
import shutil
import glob
import os


class LoggerFileTestCase(BotTestCase):

    config = dict(includes=[
        'irc3.plugins.logger',
        'irc3.plugins.userlist',
    ])

    def setUp(self):
        super(LoggerFileTestCase, self).setUp()
        self.logdir = tempfile.mkdtemp(prefix='irc3log')
        self.addCleanup(shutil.rmtree, self.logdir)

    def test_logger(self):
        bot = self.callFTU(
            **{'irc3.plugins.logger': dict(
                handler='irc3.plugins.logger.file_handler',
                filename=os.path.join(
                    self.logdir,
                    '{host}-{channel}-{date:%Y-%m-%d}.log')
            )}
        )
        filenames = os.listdir(self.logdir)
        self.assertEqual(len(filenames), 0, filenames)

        bot.dispatch(u':server 332 foo #foo :topîc')
        filenames = glob.glob(os.path.join(self.logdir, '*.log'))
        self.assertEqual(len(filenames), 1, filenames)

        with open(filenames[0]) as fd:
            self.assertIn('server has set topic to: topîc', fd.read())

        bot.dispatch(':bar!user@host JOIN #foo')
        with open(filenames[0]) as fd:
            self.assertIn('bar joined #foo', fd.read())

        bot.dispatch(':bar!user@host PRIVMSG #foo :!help')
        with open(filenames[0]) as fd:
            self.assertIn('<bar> !help', fd.read())

        bot.dispatch(':bar!user@host QUIT')
        with open(filenames[0]) as fd:
            self.assertIn('bar has quit', fd.read())

        bot.privmsg('#foo',  'youhou!')
        with open(filenames[0]) as fd:
            self.assertIn('<irc3> youhou!', fd.read())
