# -*- coding: utf-8 -*-
import configparser
import os


class IrcString(str):
    """Argument wrapper"""

    @property
    def nick(self):
        """return nick name:

        .. code-block:: py

            >>> IrcString('foo').nick
            'foo'
            >>> IrcString('foo!user@host').nick
            'foo'
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

            >>> IrcString('Foo').lnick
            'foo'
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


class Config(dict):
    """Simple dict wrapper:

    .. code-block:

        >>> c = Config(dict(a=True))
        >>> c.a
        True
    """

    def __getattr__(self, attr):
        return self[attr]


def parse_config(filename):
    filename = os.path.abspath(filename)
    here = os.path.dirname(filename)
    defaults = dict(here=here, config=filename)

    config = configparser.ConfigParser(defaults, allow_no_value=False)
    config.read([filename, os.path.expanduser('~/.irc3/passwd.ini')])

    value = {}
    for s in config.sections():
        items = {}
        for k, v in config.items(s):
            if '\n' in v:
                v = v.strip().split('\n')
            elif v.isdigit():
                v = int(v)
            elif v in ('true', 'false'):
                v = v == 'true' and True or False
            items[k] = v
        if s == 'bot':
            value.update(items)
        else:
            for k in ('here', 'config'):
                items.pop(k, '')
            value[s] = items
    return value


def maybedotted(name):
    """Resolve dotted names::

        >>> maybedotted('http.server')
        <module 'http.server' from '...'>
        >>> maybedotted('http.server.HTTPServer')
        <class 'http.server.HTTPServer'>

    ..
    """
    if not name:
        raise LookupError(
            'Not able to resolve %s' % name)
    if isinstance(name, str):
        try:
            mod = __import__(name, globals(), locals(), [''])
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
