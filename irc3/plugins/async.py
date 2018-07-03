# -*- coding: utf-8 -*-
from collections import OrderedDict
from irc3.asynchronous import AsyncEvents
from irc3 import utils
from irc3 import dec
__doc__ = """
==============================================
:mod:`irc3.plugins.async` Asynchronious events
==============================================

This module provide a way to catch data from various predefined events.

Usage
=====

You'll have to define a subclass of :class:`~irc3.asynchronous.AsyncEvents`:

.. literalinclude:: ../../irc3/plugins/async.py
  :pyobject: Whois

Notice that regexps and send_line contains some `{nick}`. This will be
substitued later with the keyword arguments passed to the instance.

Then you're able to use it in a plugin:

.. code-block:: py

    class MyPlugin:

        def __init__(self, bot):
            self.bot = bot
            self.whois = Whois(bot)

        def do_whois(self):
            # remember {nick} in the regexp? Here it is
            whois = await self.whois(nick='gawel')
            if int(whois['idle']) / 60 > 10:
                self.bot.privmsg('gawel', 'Wake up dude')

.. warning::

    Your code should always check if the result has been set before timeout by
    using `result['timeout']` which is True when the bot failed to get a result
    before 30s (you can override the default value per call)

.. warning::

    Do not over use this feature. If you're making a lot of calls at the same
    time you should experience some weird behavior since irc do not allow
    to identify responses for a command. That's why the exemple use {nick} in
    the regexp to filter events efficiently. But two concurent call for the
    same nick can still fail.

API
===

.. autoclass:: irc3.asynchronous.AsyncEvents
  :members: process_results, __call__

.. autoclass:: Async
  :members:

"""


class Whois(AsyncEvents):

    # the command will fail if we do not have a result after 30s
    timeout = 20

    # send this line before listening to events
    send_line = 'WHOIS {nick} {nick}'

    # when those events occurs, we can add them to the result list
    events = (
        # (?i) is for IGNORECASE. This will match either NicK or nick
        {'match': "(?i)^:\S+ 301 \S+ {nick} :(?P<away>.*)"},
        {'match': "(?i)^:\S+ 311 \S+ {nick} (?P<username>\S+) (?P<host>\S+) . "
                  ":(?P<realname>.*)(?i)"},
        {'match': "(?i)^:\S+ 312 \S+ {nick} (?P<server>\S+) "
                  ":(?P<server_desc>.*)"},
        {'match': "(?i)^:\S+ 317 \S+ {nick} (?P<idle>[0-9]+).*"},
        {'match': "(?i)^:\S+ 319 \S+ {nick} :(?P<channels>.*)", 'multi': True},
        {'match': "(?i)^:\S+ 330 \S+ {nick} (?P<account>\S+) "
                  ":(?P<account_desc>.*)"},
        {'match': "(?i)^:\S+ 671 \S+ {nick} :(?P<connection>.*)"},
        # if final=True then a result is returned when the event occurs
        {'match': "(?i)^:\S+ (?P<retcode>(318|401)) \S+ (?P<nick>{nick}) :.*",
         'final': True},
    )

    def process_results(self, results=None, **value):
        """take results list of all events and put them in a dict"""
        channels = []
        for res in results:
            channels.extend(res.pop('channels', '').split())
            value.update(res)
        value['channels'] = channels
        value['success'] = value.get('retcode') == '318'
        return value


class WhoChannel(AsyncEvents):

    send_line = 'WHO {channel}'

    events = (
        {"match": "(?i)^:\S+ 352 \S+ {channel} (?P<user>\S+) "
                  "(?P<host>\S+) (?P<server>\S+) (?P<nick>\S+) "
                  "(?P<modes>\S+) :(?P<hopcount>\S+) (?P<realname>.*)",
         "multi": True},
        {"match": "(?i)^:\S+ (?P<retcode>(315|401)) \S+ {channel} :.*",
         "final": True},
    )

    def process_results(self, results=None, **value):
        users = []
        for res in results:
            if 'retcode' in res:
                value.update(res)
            else:
                res['mask'] = utils.IrcString(
                    '{nick}!{user}@{host}'.format(**res))
                users.append(res)
        value['users'] = users
        value['success'] = value.get('retcode') == '315'
        return value


class WhoChannelFlags(AsyncEvents):

    flags = OrderedDict([
        ("u", "(?P<user>\S+)"),
        ("i", "(?P<ip>\S+)"),
        ("h", "(?P<host>\S+)"),
        ("s", "(?P<server>\S+)"),
        ("n", "(?P<nick>\S+)"),
        ("a", "(?P<account>\S+)"),
        ("r", ":(?P<realname>.*)"),
    ])

    send_line = "WHO {channel} c%{flags}"

    events = (
        {"match": "(?i)^:\S+ (?P<retcode>(315|401)) \S+ {channel} :.*",
         "final": True},
    )

    def process_results(self, results=None, **value):
        users = []
        for res in results:
            if 'retcode' in res:
                value.update(res)
            else:
                # Works in QuakeNet, don't know about other networks
                if res.get('account') == '0':
                    res['account'] = None
                users.append(res)
        value['users'] = users
        value['success'] = value.get('retcode') == '315'
        return value


class WhoNick(AsyncEvents):

    send_line = 'WHO {nick}'

    events = (
        {"match": "(?i)^:\S+ 352 \S+ (?P<channel>\S+) (?P<user>\S+) "
                  "(?P<host>\S+) (?P<server>\S+) (?P<nick>{nick}) "
                  "(?P<modes>\S+) :(?P<hopcount>\S+)\s*(?P<realname>.*)"},
        {"match": "(?i)^:\S+ (?P<retcode>(315|401)) \S+ {nick} :.*",
         "final": True},
    )

    def process_results(self, results=None, **value):
        for res in results:
            if 'retcode' not in res:
                res['mask'] = utils.IrcString(
                    '{nick}!{user}@{host}'.format(**res))
            value.update(res)
        value['success'] = value.get('retcode') == '315'
        return value


class IsOn(AsyncEvents):

    events = (
        {"match": "(?i)^:\S+ 303 \S+ :(?P<nicknames>({nicknames}.*|$))",
         "final": True},
    )

    def process_results(self, results=None, **value):
        nicknames = []
        for res in results:
            nicknames.extend(res.pop('nicknames', '').split())
        value['names'] = nicknames
        return value


class Topic(AsyncEvents):

    send_line = 'TOPIC {channel}{topic}'

    events = (
        {"match": ("(?i)^:\S+ (?P<retcode>(331|332|TOPIC))"
                   "(:?\s+\S+\s+|\s+){channel} :(?P<topic>.*)"),
         "final": True},
    )

    def process_results(self, results=None, **value):
        for res in results:
            status = res.get('retcode', '')
            if status.upper() in ('332', 'TOPIC'):
                value['topic'] = res.get('topic')
            else:
                value['topic'] = None
            return value


class Names(AsyncEvents):

    send_line = 'NAMES {channel}'

    events = (
        {"match": "(?i)^:\S+ 353 .*{channel} :(?P<nicknames>.*)",
         'multi': True},
        {'match': "(?i)^:\S+ (?P<retcode>(366|401)) \S+ {channel} :.*",
         'final': True},
    )

    def process_results(self, results=None, **value):
        nicknames = []
        for res in results:
            nicknames.extend(res.pop('nicknames', '').split())
        value['names'] = nicknames
        value['success'] = value.get('retcode') == '366'
        return value


class ChannelBans(AsyncEvents):

    send_line = 'MODE {channel} +b'

    events = (
        {"match": "(?i)^:\S+ 367 \S+ {channel} (?P<mask>\S+) (?P<user>\S+) "
                  "(?P<timestamp>\d+)",
         "multi": True},
        {"match": "(?i)^:\S+ 368 \S+ {channel} :.*",
         "final": True},
    )

    def process_results(self, results=None, **value):
        bans = []
        for res in results:
            # TODO: fix event so this one isn't needed
            if not res:
                continue
            res['timestamp'] = int(res['timestamp'])
            bans.append(res)
        value['bans'] = bans
        return value


class CTCP(AsyncEvents):

    send_line = 'PRIVMSG {nick} :\x01{ctcp}\x01'

    events = (
        {"match": "(?i):(?P<mask>\S+) NOTICE \S+ :\x01(?P<ctcp>\S+) "
                  "(?P<reply>.*)\x01",
         "final": True},
        {"match": "(?i)^:\S+ (?P<retcode>486) \S+ :(?P<reply>.*)",
         "final": True}
    )

    def process_results(self, results=None, **value):
        """take results list of all events and return first dict"""
        for res in results:
            if 'mask' in res:
                res['mask'] = utils.IrcString(res['mask'])
            value['success'] = res.pop('retcode', None) != '486'
            value.update(res)
        return value


@dec.plugin
class Async:
    """Asynchronious plugin.
    Extend the bot with some common commands using
    :class:`~irc3.asynchronous.AsyncEvents`
    """

    def __init__(self, context):
        self.context = context
        self.context.async_cmds = self
        self.async_whois = Whois(context)
        self.async_who_channel = WhoChannel(context)
        self.async_who_nick = WhoNick(context)
        self.async_topic = Topic(context)
        self.async_ison = IsOn(context)
        self.async_names = Names(context)
        self.async_channel_bans = ChannelBans(context)
        self.async_ctcp = CTCP(context)

    def async_who_channel_flags(self, channel, flags, timeout):
        """
        Creates and calls a class from WhoChannelFlags with needed match rule
        for WHO command on channels with flags.
        """
        # Lowercase flags and sort based on WhoChannelFlags.flags, otherwise
        # resulting dict is wrong. Also join flags if it's a sequence.
        flags = ''.join([f.lower() for f in WhoChannelFlags.flags
                         if f in flags])
        regex = [WhoChannelFlags.flags[f] for f in flags]
        channel = channel.lower()
        cls = type(
            WhoChannelFlags.__name__,
            (WhoChannelFlags,),
            {"events": WhoChannelFlags.events + (
                {"match": "(?i)^:\S+ 354 \S+ {0}".format(' '.join(regex)),
                 "multi": True},
            )}
        )
        return cls(self.context)(channel=channel, flags=flags, timeout=timeout)

    @dec.extend
    def whois(self, nick, timeout=20):
        """Send a WHOIS and return a Future which will contain recieved data:

        .. code-block:: py

            result = await bot.async_cmds.whois('gawel')
        """
        return self.async_whois(nick=nick.lower(), timeout=timeout)

    @dec.extend
    def who(self, target, flags=None, timeout=20):
        """Send a WHO and return a Future which will contain recieved data:

        .. code-block:: py

            result = await bot.async_cmds.who('gawel')
            result = await bot.async_cmds.who('#irc3')
            result = await bot.async_cmds.who('#irc3', 'an')
            # or
            result = await bot.async_cmds.who('#irc3', ['a', 'n'])
        """
        target = target.lower()
        if target.startswith('#'):
            if flags:
                return self.async_who_channel_flags(channel=target,
                                                    flags=flags,
                                                    timeout=timeout)
            return self.async_who_channel(channel=target, timeout=timeout)
        else:
            return self.async_who_nick(nick=target, timeout=timeout)

    def topic(self, channel, topic=None, timeout=20):
        if not topic:
            topic = ''
        else:
            topic = ' ' + topic.strip()
        return self.async_topic(channel=channel, topic=topic, timeout=timeout)

    @dec.extend
    def ison(self, *nicknames, **kwargs):
        """Send a ISON and return a Future which will contain recieved data:

        .. code-block:: py

            result = await bot.async_cmds.ison('gawel', 'irc3')
        """
        nicknames = [n.lower() for n in nicknames]
        self.context.send_line('ISON :{0}'.format(' '.join(nicknames)))
        return self.async_ison(nicknames='(%s)' % '|'.join(nicknames),
                               **kwargs)

    @dec.extend
    def names(self, channel, timeout=20):
        """Send a NAMES and return a Future which will contain recieved data:

        .. code-block:: py

            result = await bot.async_cmds.names('#irc3')
        """
        return self.async_names(channel=channel.lower(), timeout=timeout)

    @dec.extend
    def channel_bans(self, channel, timeout=20):
        """Send a MODE +b and return a Future which will contain recieved data:
        .. code-block:: py
            result = await bot.async_cmds.channel_bans('#irc3')
        """
        return self.async_channel_bans(channel=channel.lower(),
                                       timeout=timeout)

    @dec.extend
    def ctcp_async(self, nick, ctcp, timeout=20):
        """Send a CTCP and return a Future which will contain recieved data:

        .. code-block:: py

            result = await bot.async_cmds.ctcp('irc3', 'version')
        """
        return self.async_ctcp(nick=nick, ctcp=ctcp.upper(), timeout=timeout)
