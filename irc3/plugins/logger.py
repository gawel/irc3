# -*- coding: utf-8 -*-
import os
import irc3
import logging
import codecs
from datetime import datetime
__doc__ = '''
================================================
:mod:`irc3.plugins.logger` Channel logger plugin
================================================

Log channels

..
    >>> from irc3.testing import IrcBot

Usage::

    >>> bot = IrcBot(**{
    ...     'irc3.plugins.logger': {
    ...         'handler': 'irc3.plugins.logger.file_handler',
    ...     },
    ... })
    >>> bot.include('irc3.plugins.logger')


Available handlers:

.. autoclass:: file_handler
'''


class file_handler:
    """Write logs to file in ~/.irc3/logs
    """

    formatters = {
        'privmsg': '{date:%H:%M} <{mask.nick}> {data}',
        'join': '{date:%H:%M} {mask.nick} joined {channel}',
        'part': '{date:%H:%M} {mask.nick} has left {channel} ({data})',
        'quit': '{date:%H:%M} {mask.nick} has quit ({data})',
        'topic': '{date:%H:%M} {mask.nick} has set topic to: {data}',
    }

    def __init__(self, bot):
        config = {
            'filename': '~/.irc3/logs/{host}/{channel}-{date:%Y-%m-%d}.log',
            'channels': [],
        }
        config.update(bot.config.get(__name__, {}))
        self.filename = config['filename']
        self.encoding = bot.encoding
        self.formatters = bot.config.get(
            __name__ + '.formatters',
            self.formatters)

    def __call__(self, event):
        filename = self.filename.format(**event)
        if not os.path.isfile(filename):
            dirname = os.path.dirname(filename)
            if not os.path.isdir(dirname):  # pragma: no cover
                os.makedirs(dirname)
        fmt = self.formatters.get(event['event'].lower())
        if fmt:
            with codecs.open(filename, 'a+', self.encoding) as fd:
                fd.write(fmt.format(**event) + '\r\n')


@irc3.plugin
class Logger:
    """Logger plugin. Use the :class:~file_handler handler by default
    """

    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config.get(__name__, {})
        self.log = logging.getLogger(__name__)
        hdl = irc3.utils.maybedotted(self.config.get('handler', file_handler))
        self.log.debug('Handler: %s', hdl.__name__)
        self.handler = hdl(bot)

    def process(self, **kwargs):
        kw = dict(host=self.bot.config.host, date=datetime.now(),
                  **kwargs)
        self.handler(kw)

    @irc3.event((r'''(@(?P<tags>\S+) )?:(?P<mask>\S+) (?P<event>[A-Z]+)'''
                 r''' (?P<target>#\S+)(\s:(?P<data>.*)|$)'''))
    def on_input(self, mask, event, target=None, data=None, **kwargs):
        if target and target.is_channel:
            self.process(event=event, mask=mask,
                         channel=target, data=data, **kwargs)

    @irc3.event((r'''(@(?P<tags>\S+) )?(?P<event>[A-Z]+) (?P<target>#\S+)'''
                 r'''(\s:(?P<data>.*)|$)'''), iotype='out')
    def on_output(self, event, target=None, data=None, **kwargs):
        if target and target.is_channel:
            self.process(event=event, mask=irc3.utils.IrcString(self.bot.nick),
                         channel=target, data=data, **kwargs)

    @irc3.event(irc3.rfc.JOIN_PART_QUIT)
    def on_quit(self, mask, event, channel=None, data=None, **kwargs):
        if event.lower() == 'quit':
            channels = getattr(self.bot, 'channels', None)
            if channels:
                nick = mask.nick
                for name, channel in channels.items():
                    if nick in channel:
                        self.process(event=event, mask=mask,
                                     channel=name, data=data, **kwargs)

    @irc3.event(irc3.rfc.RPL_TOPIC)
    def on_topic(self, srv=None, **kwargs):
        self.process(event='TOPIC', mask=srv, **kwargs)
