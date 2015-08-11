# -*- coding: utf-8 -*-
from irc3.compat import text_type
import functools
import string
import irc3
__doc__ = '''
================================================
:mod:`irc3.plugins.casefold` casefolding plugin
================================================

This command introduces a `bot.casefold` function that casefolds strings based
on the current casemapping of the IRC server.

This lets you casefold nicks and channel names so that on a server using
rfc1459 casemapping, `#cool[chan]` and `#Cool{Chan}` are seen as the same
channel.

..
    >>> from irc3.testing import IrcBot
    >>> from irc3.testing import ini2config

Usage::

    >>> config = ini2config("""
    ... [bot]
    ... includes =
    ...     irc3.plugins.casefold
    ... """)
    >>> bot = IrcBot(**config)

Returning casefolded strings::

    >>> bot.casefold('ThisIsANick')
    'thisisanick'
    >>> bot.casefold('#WeirdChannelNames[]')
    '#weirdchannelnames{}'
'''


@irc3.plugin
class Casefold(object):

    def __init__(self, bot):
        self.bot = bot
        self.recalculate_casemaps()
        self.bot.casefold = functools.partial(self.casefold)

    # casemapping
    @irc3.event(r'^:\S+ 005 \S+ .+CASEMAPPING.*')
    def recalculate_casemaps(self):
        casemapping = self.bot.config['server_config'].get('CASEMAPPING',
                                                           'rfc1459')

        if casemapping == 'rfc1459':
            lower_chars = (string.ascii_lowercase +
                           ''.join(chr(i) for i in range(123, 127)))
            upper_chars = (string.ascii_uppercase +
                           ''.join(chr(i) for i in range(91, 95)))

        elif casemapping == 'ascii':
            lower_chars = string.ascii_lowercase
            upper_chars = string.ascii_uppercase

        table_in = (ord(char) for char in upper_chars)
        self._lower_trans = dict(zip(table_in, text_type(lower_chars)))
        return

    def casefold(self, in_str):
        """Casefold the given string, with the current server's casemapping."""
        is_str = isinstance(in_str, str)
        folded = text_type(in_str).translate(self._lower_trans)
        if is_str:
            return str(folded)
        return folded
