# -*- coding: utf-8 -*-
from unicodedata import normalize
from .compat import asyncio
from . import tags
import configparser
import importlib
import functools
import textwrap
import logging
import os
import re

try:
    BaseString = unicode
except NameError:  # pragma: no cover
    BaseString = str


def slugify(value):
    if not isinstance(value, BaseString):  # pragma: no cover
        value = value.decode('utf8', 'ignore')
    value = normalize('NFKD', value)
    value = value.encode('ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s\.-]', '', value).strip().lower()
    value = re.sub('[-\s]+', '-', value)
    value = re.sub('-*\.+-*', '.', value)
    return value


class IrcString(BaseString):
    """Argument wrapper"""

    @property
    def nick(self):
        """return nick name:

        .. code-block:: py

            >>> print(IrcString('foo').nick)
            foo
            >>> print(IrcString('foo!user@host').nick)
            foo
            >>> IrcString('#foo').nick is None
            True
            >>> IrcString('irc.freenode.net').nick is None
            True
        """
        if '!' in self:
            return self.split('!', 1)[0]
        if not self.is_channel and not self.is_server:
            return self

    @property
    def lnick(self):
        """return nick name in lowercase:

        .. code-block:: py

            >>> print(IrcString('Foo').lnick)
            foo
        """
        nick = self.nick
        if nick:
            return nick.lower()

    @property
    def host(self):
        if '!' in self:
            return self.split('!', 1)[1]

    @property
    def is_user(self):
        return '!' in self

    @property
    def is_channel(self):
        """return True if the string is a channel:

        .. code-block:: py

            >>> IrcString('#channel').is_channel
            True
            >>> IrcString('&channel').is_channel
            True
        """
        return self.startswith(('#', '&'))

    @property
    def is_server(self):
        """return True if the string is a server:

        .. code-block:: py

            >>> IrcString('irc.freenode.net').is_server
            True
        """
        if self == '*':
            return True
        return '!' not in self and '.' in self

    @property
    def is_nick(self):
        """return True if the string is a nickname:

        .. code-block:: py

            >>> IrcString('foo').is_nick
            True
        """
        return not (self.is_server or self.is_channel)

    @property
    def tagdict(self):
        """return a dict converted from this string interpreted as a tag-string

        .. code-block:: py

            >>> from pprint import pprint
            >>> dict_ = IrcString('aaa=bbb;ccc;example.com/ddd=eee').tagdict
            >>> pprint({str(k): str(v) for k, v in dict_.items()})
            {'aaa': 'bbb', 'ccc': 'None', 'example.com/ddd': 'eee'}
        """
        tagdict = getattr(self, '_tagdict', None)
        if tagdict is None:
            try:
                self._tagdict = tags.decode(self)
            except ValueError:
                self._tagdict = {}
        return self._tagdict


STRIPPED_CHARS = '\t '


def split_message(message, max_length):
    """Split long messages"""
    if len(message) > max_length:
        for message in textwrap.wrap(message, max_length):
            yield message
    else:
        yield message.rstrip(STRIPPED_CHARS)


class Config(dict):
    """Simple dict wrapper:

    .. code-block:: python

        >>> c = Config(dict(a=True))
        >>> c.a
        True
    """

    def __getattr__(self, attr):
        return self[attr]


def parse_config(main_section, *filenames):
    """parse config files"""
    filename = filenames[-1]
    filename = os.path.abspath(filename)
    here = os.path.dirname(filename)
    defaults = dict(here=here, hash='#')

    config = configparser.ConfigParser(
        defaults, allow_no_value=False,
        interpolation=configparser.ExtendedInterpolation(),
    )
    config.optionxform = str
    config.read([os.path.expanduser('~/.irc3/passwd.ini')] + list(filenames))

    value = {}
    for s in config.sections():
        items = {}
        for k, v in config.items(s):
            if '\n' in v:
                v = as_list(v)
            elif v.isdigit():
                v = int(v)
            elif v.lstrip('.').isdigit():
                v = float(v)
            elif v in ('true', 'false'):
                v = v == 'true' and True or False
            items[k] = v
        if s == main_section:
            value.update(items)
        else:
            for k in ('here', 'config'):
                items.pop(k, '')
            value[s] = items
    value.update(defaults)
    value['configfiles'] = filenames
    return value


def extract_config(config, prefix):
    """return all keys with the same prefix without the prefix"""
    prefix = prefix.strip('.') + '.'
    plen = len(prefix)
    value = {}
    for k, v in config.items():
        if k.startswith(prefix):
            value[k[plen:]] = v
    return value


def as_list(value):
    """clever string spliting:

    .. code-block:: python

        >>> print(as_list('value'))
        ['value']
        >>> print(as_list('v1 v2'))
        ['v1', 'v2']
        >>> print(as_list(None))
        []
        >>> print(as_list(['v1']))
        ['v1']
    """
    if isinstance(value, (list, tuple)):
        return value
    if not value:
        return []
    for c in '\n ':
        if c in value:
            value = value.split(c)
            return [v.strip() for v in value if v.strip()]
    return [value]


def as_channel(value):
    """Always return a channel name:

    .. code-block:: python

        >>> print(as_channel('chan'))
        #chan
        >>> print(as_channel('#chan'))
        #chan
        >>> print(as_channel('&chan'))
        &chan
    """
    if not value.startswith(('#', '&')):
        return '#' + value
    return value


def parse_modes(modes, targets=None, noargs=''):
    """Parse channel modes:

    .. code-block:: python

        >>> parse_modes('+c-n', noargs='cn')
        [('+', 'c', None), ('-', 'n', None)]
        >>> parse_modes('+c-v', ['gawel'], noargs='c')
        [('+', 'c', None), ('-', 'v', 'gawel')]
    """
    if not targets:
        targets = []
    cleaned = []
    for mode in modes:
        if mode in '-+':
            char = mode
            continue
        target = targets.pop(0) if mode not in noargs else None
        cleaned.append((char, mode, target))
    return cleaned


def wraps_with_context(func, context):
    """Return a wrapped partial(func, context)"""
    wrapped = functools.partial(func, context)
    wrapped = functools.wraps(func)(wrapped)
    if asyncio.iscoroutinefunction(func):
        wrapped = asyncio.coroutine(wrapped)
    return wrapped


def maybedotted(name):
    """Resolve dotted names:

    .. code-block:: python

        >>> maybedotted('irc3.config')
        <module 'irc3.config' from '...'>
        >>> maybedotted('irc3.utils.IrcString')
        <class 'irc3.utils.IrcString'>

    ..
    """
    if not name:
        raise LookupError(
            'Not able to resolve %s' % name)
    if not hasattr(name, '__name__'):
        try:
            mod = importlib.import_module(name)
        except ImportError:
            attr = None
            if '.' in name:
                names = name.split('.')
                attr = names.pop(-1)
                try:
                    mod = maybedotted('.'.join(names))
                except LookupError:
                    attr = None
                else:
                    attr = getattr(mod, attr, None)
            if attr is not None:
                return attr
            raise LookupError(
                'Not able to resolve %s' % name)
        else:
            return mod
    return name


class Handler(logging.Handler):

    def __init__(self, bot, *targets):
        super(Handler, self).__init__()
        self.bot = bot
        self.targets = targets

    def yield_records(self, record):
        for record in self.format(record).split('\n'):
            for t in self.targets:
                yield t, record

    def emit(self, record):
        self.bot.call_many('privmsg', self.yield_records(record))


class Logger(logging.getLoggerClass()):
    """Replace the default logger to add a set_irc_targets() method"""

    def set_irc_targets(self, bot, *targets):
        """Add a irc Handler using bot and log to targets (can be nicks or
        channels:

        ..
            >>> bot = None

        .. code-block:: python

            >>> log = logging.getLogger('irc.mymodule')
            >>> log.set_irc_targets(bot, '#chan', 'admin')
        """
        # get formatter initialized by config (usualy on a NullHandler)
        l = logging.getLogger('irc')
        formatter = l.handlers[0].formatter
        # add a handler for the sub logger
        handler = Handler(bot, *targets)
        handler.setFormatter(formatter)
        self.addHandler(handler)

logging.setLoggerClass(Logger)
