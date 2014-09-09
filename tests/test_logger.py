# -*- coding: utf-8 -*-
from irc3.testing import BotTestCase, mock
from unittest import SkipTest
import tempfile
import shutil
import glob
import os
from freezegun import freeze_time
try:
    from moto import mock_s3
    import boto
except ImportError:
    mock_s3 = lambda x: x
    boto = None


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

        bot.dispatch(':server 332 foo #foo :topic')
        filenames = glob.glob(os.path.join(self.logdir, '*.log'))
        self.assertEqual(len(filenames), 1, filenames)

        with open(filenames[0]) as fd:
            self.assertIn('server has set topic to: topic', fd.read())

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


class LoggerS3NullTestCase(BotTestCase):
    config = {
        "nick": "myircbot",
        "host": "irc.testing.net",
        "includes": [
            'irc3.plugins.logger',
            'irc3.plugins.userlist',
        ],
    }

    @mock.patch('irc3.plugins.logger.boto', None)
    def test_no_boto(self):
        with self.assertRaises(ImportError):
            self.callFTU(
                **{'irc3.plugins.logger': dict(
                    handler='irc3.plugins.logger.s3_handler',
                )}
            )


class LoggerS3TestCase(LoggerS3NullTestCase):
    def setUp(self):
        super(LoggerS3NullTestCase, self).setUp()
        if not boto:
            raise SkipTest("missing dependency: boto")

        self.bot = self.callFTU(
            **{'irc3.plugins.logger': dict(
                handler='irc3.plugins.logger.s3_handler',
            )}
        )

    @mock_s3
    @freeze_time("2014-01-04")
    def test_message(self):
        self.bot.dispatch(':server 332 foo #foo :topic')
        conn = boto.connect_s3()
        bucket = conn.get_bucket("irc3-myircbot")
        key = bucket.get_key("irc.testing.net/#foo-2014-01-04.log")
        self.assertIn(
            'server has set topic to: topic\r\n',
            key.get_contents_as_string().decode('utf8')
        )
