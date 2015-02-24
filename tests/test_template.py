# -*- coding: utf-8 -*-
from irc3.testing import BotTestCase
from irc3.template import main
from irc3 import utils
from shutil import rmtree
import tempfile
import sys
import os


class Template(BotTestCase):

    def setUp(self):
        self.wd = tempfile.mkdtemp(prefix='irc3-template')
        self.addCleanup(os.chdir, os.getcwd())
        self.addCleanup(rmtree, self.wd)
        self.addCleanup(sys.path.remove, self.wd)
        sys.path.append(self.wd)
        os.chdir(self.wd)

    def test_template(self):
        main(nick='mybot')
        files = sorted(os.listdir(self.wd))
        assert files == ['config.ini', 'mybot_plugin.py']
        config = utils.parse_config('bot', 'config.ini')
        bot = self.callFTU(**config)
        bot.dispatch(':gawel!n@h JOIN #mybot')
        self.assertSent(['PRIVMSG #mybot :Hi gawel!'])
        bot.dispatch(':yournick!n@h PRIVMSG #mybot :!echo Hi!')
        self.assertSent(['PRIVMSG #mybot :Hi!'])
