# -*- coding: utf-8 -*-
from re import compile
from ._rfc import *  # NOQA

_re_params = compile(r'P<([^>]+)>')


def _extract_params(regexp):
    """extract parameters from regexp"""
    params = _re_params.findall(regexp)
    if params and params[0] == 'tags':
        params.pop(0)
        params.append('tags')
    return params


class raw(str):
    name = None
    re = None
    re_out = None
    server = None

    @classmethod
    def new(cls, name, regexp, regexp_out=None):
        r = cls(name)
        r.name = name
        r.re = regexp
        r.params = _extract_params(r.re)
        if regexp_out is not None:
            out_name = 'OUT_' + name
            r.re_out = cls(out_name)
            r.re_out.name = out_name
            r.re_out.re = regexp_out
            r.re_out.params = _extract_params(regexp_out)
        if regexp.startswith((':', '^:', '(@', '^(@')):
            name = 'SERVER_' + name
            r.server = cls(name)
            r.server.name = name
            if regexp.startswith(('(@', '^(@')):
                r.server.re = regexp.split(' ', 2)[2]
                r.server.re = r'(@(?P<tags>\S+) )?' + r.server.re
            else:
                r.server.re = regexp.split(' ', 1)[1]
        return r


CONNECTED = raw.new('CONNECTED',
                    r'^:(?P<srv>\S+) (376|422) (?P<me>\S+) :(?P<data>.*)')

PING = raw.new('PING', r'^PING :?(?P<data>.*)')
PONG = raw.new(
    'PONG',
    r'^(@(?P<tags>\S+) )?:(?P<server>\S+) PONG (?P=server) :?(?P<data>.*)')

NEW_NICK = raw.new(
    'NEW_NICK',
    regexp=r'^(@(?P<tags>\S+) )?:(?P<nick>\S+) NICK :?(?P<new_nick>\S+)',
    regexp_out=r'^NICK :?(?P<new_nick>\S+)',
)

JOIN = raw.new(
    'JOIN',
    regexp=r'^(@(?P<tags>\S+) )?:(?P<mask>\S+) JOIN :?(?P<channel>\S+)',
    regexp_out=r'^JOIN :?(?P<channel>\S+)',
)

PART = raw.new(
    'PART',
    regexp=(
        r'^(@(?P<tags>\S+) )?:(?P<mask>\S+) '
        r'PART (?P<channel>\S+)(\s+:(?P<data>.*)|$)'),
    regexp_out=r'PART (?P<channel>\S+)(\s+:(?P<data>.*)|$)',
)

QUIT = raw.new(
    'QUIT',
    regexp=r'^(@(?P<tags>\S+) )?:(?P<mask>\S+) QUIT(\s+:(?P<data>.*)|$)',
    regexp_out=r'^QUIT(\s+:(?P<data>.*)|$)',
)

JOIN_PART_QUIT = raw.new(
    'JOIN_PART_QUIT',
    regexp=(
        r'^(@(?P<tags>\S+) )?:(?P<mask>\S+) '
        r'(?P<event>JOIN|PART|QUIT)\s*:*(?P<channel>\S*)(\s+:(?P<data>.*)|$)'),
    regexp_out=(
        r'^(?P<event>JOIN|PART|QUIT)\s*:*(?P<channel>\S*)(\s+:(?P<data>.*)|$)')
)

KICK = raw.new(
    'KICK',
    regexp=(
        r'^(@(?P<tags>\S+) )?:(?P<mask>\S+) '
        r'(?P<event>KICK)\s+(?P<channel>\S+)\s*(?P<target>\S+)'
        r'(\s+:(?P<data>.*)|$)'),
    regexp_out=(
        r'^(?P<event>KICK)\s+(?P<channel>\S+)\s*(?P<target>\S+)'
        r'(\s+:(?P<data>.*)|$)'),
)

MODE = raw.new(
    'MODE',
    regexp=(
        r'^(@(?P<tags>\S+) )?:(?P<mask>\S+) (?P<event>MODE)\s+'
        r'(?P<target>\S+)\s+(?P<modes>\S+)(\s+(?P<data>.*)|$)'),
    regexp_out=(
        r'^(?P<event>MODE)\s+'
        r'(?P<target>\S+)\s+(?P<modes>\S+)(\s+(?P<data>.*)|$)'),
)

MY_PRIVMSG = raw.new(
    'MY_PRIVMSG',
    regexp=(
        r'^(@(?P<tags>\S+) )?:(?P<mask>\S+!\S+@\S+) '
        r'(?P<event>(PRIVMSG|NOTICE)) '
        r'(?P<target>(#\S+|{nick})) :{nick}[:,\s]\s*'
        r'(?P<data>\S+.*)$'),
    regexp_out=(
        r'^(?P<event>(PRIVMSG|NOTICE)) (?P<target>\S+) :(?P<data>.*)$')
)

PRIVMSG = raw.new(
    'PRIVMSG',
    regexp=(
        r'^(@(?P<tags>\S+) )?:(?P<mask>\S+!\S+@\S+) '
        r'(?P<event>(PRIVMSG|NOTICE)) '
        r'(?P<target>\S+) :(?P<data>.*)$'),
)
PRIVMSG.re_out = MY_PRIVMSG.re_out

CTCP = raw.new(
    'CTCP',
    regexp=(
        '^(@(?P<tags>\S+) )?:(?P<mask>\S+!\S+@\S+) '
        '(?P<event>(PRIVMSG|NOTICE)) '
        '{nick} :\x01(?P<ctcp>.*)\x01$'),
    regexp_out=(
        '^(?P<event>(PRIVMSG|NOTICE)) (?P<target>\S+) :\x01(?P<ctcp>.*)\x01$'
    ),
)

INVITE = raw.new(
    'INVITE',
    regexp=(
        r'^(@(?P<tags>\S+) )?:(?P<mask>\S+!\S+@\S+) '
        r'INVITE {nick} :?(?P<channel>\S+)$')
)

TOPIC = raw.new(
    'TOPIC',
    regexp=(
        r'^(@(?P<tags>\S+) )?:(?P<mask>\S+!\S+@\S+) '
        r'TOPIC (?P<channel>\S+) :(?P<data>.*)$'),
    regexp_out=(
        r'^TOPIC (?P<channel>\S+) :(?P<data>.*)$'),
)

ERR_NICK = raw.new(
    'ERR_NICK',
    "^(@(?P<tags>\S+) )?:(?P<srv>\S+) (?P<retcode>(432|433|436)) (?P<me>\S+) "
    "(?P<nick>\S+) :(?P<data>.*)")
