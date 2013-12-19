# -*- coding: utf-8 -*-
__doc__ = '''
==========================================
:mod:`irc3.plugin.human` Human plugin
==========================================

Store public message addressed to the bot in a file and reply a random message
extracted from this file.

..
    >>> from irc3 import IrcBot
    >>> IrcBot.defaults.update(async=False, testing=True)
    >>> with open('/tmp/human.db', 'wb') as fd:
    ...     s = fd.write(b'Yo!\\nYo!\\nYo!\\nYo!\\n')

Register the plugin::

    >>> from irc3 import IrcBot
    >>> bot = IrcBot(human='/tmp/human.db', nick='nono')
    >>> bot.include('irc3.plugins.human')

And it should work::

    >>> bot.test(':foo!m@h PRIVMSG #chan :nono: Yo!')
    >>> bot.sent
    ['PRIVMSG #chan :foo: Yo!']

'''
import os
import irc3
import stat
import codecs
import random
import subprocess


@irc3.plugin
class Human:

    def __init__(self, bot):
        self.bot = bot
        self.db = os.path.expanduser(
            bot.config.get('human', '~/.irc3/human.db'))
        try:
            os.makedirs(os.path.dirname(self.db))
        except OSError:
            pass
        if not os.path.isfile(self.db):  # pragma: no cover
            self.initialize(15)

    def initialize(self, amount):  # pragma: no cover
        cmd = (
            'wget -q -t 1 -O- '
            '"http://www.iheartquotes.com/api/v1/random?max_lines=1" '
            '| head -n 1 | grep -v "&" >> {}').format(self.db)
        processes = [subprocess.Popen(cmd, shell=True) for i in range(amount)]
        for p in processes:
            p.wait()

    @irc3.event((r':(?P<mask>\S+) PRIVMSG (?P<target>#\S+) '
                 r':%(nick)s.(\s+(?P<data>\w+.*)|$)'))
    def on_channel_message(self, mask=None, target=None, data=None):
        with codecs.open(self.db, 'ab+', encoding=self.bot.encoding) as fd:
            fd.write(data + '\n')

        pos = random.randint(0, os.stat(self.db)[stat.ST_SIZE])
        with codecs.open(self.db, encoding=self.bot.encoding) as fd:
            fd.seek(pos)
            fd.readline()
            try:
                message = fd.readline().strip()
            except:  # pragma: no cover
                pass

        message = message or 'Yo!'
        self.bot.privmsg(target, '{0}: {1}'.format(mask.nick, message))
