# -*- coding: utf-8 -*-
import irc3
import base64
__doc__ = '''
===================================================
:mod:`irc3.plugins.sasl` SASL authentification
===================================================

Allow to use sasl authentification

..
    >>> from irc3.testing import IrcBot
    >>> from irc3.testing import ini2config

Usage::

    >>> config = ini2config("""
    ... [bot]
    ... sasl_username = irc3
    ... sasl_password = passwd
    ... """)
    >>> bot = IrcBot(**config)

'''


@irc3.plugin
class Sasl:

    def __init__(self, bot):
        self.bot = bot
        self.events = [
            irc3.event(r'^:\S+ CAP \S+ LS :(?P<data>.*)', self.cap_ls),
            irc3.event(r'^:\S+ CAP \S+ ACK :.*sasl.*', self.cap_ack),
            irc3.event(r'AUTHENTICATE +', self.authenticate),
            irc3.event(r'^:\S+ 903 \S+ :SASL authentication successful',
                       self.cap_end),
        ]

    def connection_ready(self, *args, **kwargs):
        self.bot.send('CAP LS\r\n')
        self.bot.attach_events(*self.events)

    def cap_ls(self, data=None, **kwargs):
        if 'sasl' in data.lower():
            self.bot.send_line('CAP REQ :sasl')
        else:
            self.cap_end()

    def cap_ack(self, **kwargs):
        self.bot.send_line('AUTHENTICATE PLAIN')

    def authenticate(self, **kwargs):
        auth = ('{sasl_username}\0'
                '{sasl_username}\0'
                '{sasl_password}').format(**self.bot.config)
        auth = base64.encodestring(auth.encode('utf8'))
        auth = auth.decode('utf8').rstrip('\n')
        self.bot.send_line('AUTHENTICATE ' + auth)

    def cap_end(self, **kwargs):
        self.bot.send_line('CAP END')
        self.bot.detach_events(*self.events)
