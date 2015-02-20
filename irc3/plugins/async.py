# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from irc3.async import AsyncEvents
from irc3 import dec
__doc__ = """
==============================================
:mod:`irc3.plugins.async` Asynchronious events
==============================================

This module provide a way to catch data from various predefined events.

Usage
=====

You'll have to define a subclass of :class:`~irc3.async.AsyncEvents`:

.. literalinclude:: ../../irc3/plugins/async.py
  :pyobject: Whois

Notice that the regexp contain some `{nick}`. This will be substitued later by
the keyword arguments passed to the instance.

Then you're able to use it in a plugin:

.. code-block:: py

    class MyPlugin(object):

        def __init__(self, bot):
            self.bot = bot
            self.whois = Whois(context)

        def do_whois(self):
            self.bot.send_line('WHOIS gawel gawel')
            # remember {nick} in the regexp? Here it is
            whois = yield from self.whois(nick='gawel')
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

.. autoclass:: irc3.async.AsyncEvents
  :members: process_results, __call__

.. autoclass:: Async
  :members:

"""


class Whois(AsyncEvents):
    """Catch whois related events"""

    # the command will fail if we do not have a result after 30s
    timeout = 30

    # when those events occurs, we can set/return the result list
    # (?i) is for IGNORECASE. This will match either NicK or nick
    events = [r"(?i)^:\S+ (?P<retcode>(318|401)) \S+ (?P<nick>{nick}) :.*"]

    # when those events occurs, we add then to the future result list
    extra_events = [
        "(?i)^:\S+ 301 \S+ {nick} :(?P<away>.*)",
        "(?i)^:\S+ 311 \S+ {nick} (?P<username>\S+) (?P<host>\S+) . "
        ":(?P<realname>.*)(?i)",
        "(?i)^:\S+ 317 \S+ {nick} (?P<idle>[0-9]+).*",
        "(?i)^:\S+ 319 \S+ {nick} :(?P<channels>.*)",
    ]

    def process_results(self, results=None, **value):
        """take result list of all events and put them in a dict"""
        channels = []
        for res in results:
            channels.extend(res.pop('channels', '').split())
            value.update(res)
        value['channels'] = channels
        value['success'] = value.get('retcode') == '318'
        return value


class IsOn(AsyncEvents):

    events = ["(?i)^:\S+ 303 \S+ :(?P<nicknames>({nicknames}.*|$))"]

    def process_results(self, results=None, **value):
        nicknames = []
        for res in results:
            nicknames.extend(res.pop('nicknames', '').split())
        value['nicknames'] = nicknames
        return value


@dec.plugin
class Async(object):
    """Asynchronious plugin.
    Extend the bot with some common commands using
    :class:`~irc3.async.AsyncEvents`
    """

    def __init__(self, context):
        self.context = context
        self.ison = IsOn(context)
        self.whois = Whois(context)

    @dec.extend
    def async_whois(self, nick, timeout=20):
        """Send a WHOIS and return a Future which will contain recieved data:

        .. code-block:: py

            result = yield from bot.async_whois('gawel')
        """
        self.context.send_line('WHOIS {0} {0}'.format(nick))
        return self.whois(nick=nick.lower(), timeout=timeout)

    @dec.extend
    def async_ison(self, *nicknames, **kwargs):
        """Send a ISON and return a Future which will contain recieved data:

        .. code-block:: py

            result = yield from bot.async_ison('gawel')
        """
        timeout = kwargs.get('timeout')
        self.context.send_line('ISON :{0}'.format(' '.join(nicknames)))
        return self.ison(nicknames='(%s)' % '|'.join(nicknames),
                         timeout=timeout)
