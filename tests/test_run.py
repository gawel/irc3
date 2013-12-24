# -*- coding: utf-8 -*-
from unittest import TestCase
from docopt import DocoptExit
from irc3 import run


class TestRun(TestCase):

    def callFTU(self, *args):
        return run(args)

    def test_args_error(self):
        self.assertRaises(DocoptExit, self.callFTU, '-x')

    def test_configfile(self):
        bot = self.callFTU('-dr', 'examples/bot.ini')
        self.assertEqual(bot.config.autojoins, ['irc3'])
