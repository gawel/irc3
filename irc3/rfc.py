# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from ._rfc import *  # NOQA


class raw(str):
    name = None
    re = None
    server = None

    @classmethod
    def new(cls, name, regexp):
        r = cls(name)
        r.name = name
        r.re = regexp
        if regexp.startswith((':', '^:')):
            name = 'SERVER_' + name
            r.server = cls(name)
            r.server.name = name
            r.server.re = regexp.split(' ', 1)[1]
        return r

CONNECTED = raw.new('CONNECTED',
                    r'^:(?P<srv>\S+) (376|422) (?P<me>\S+) :(?P<data>.*)')

PING = raw.new('PING', r'^PING :?(?P<data>.*)')
PONG = raw.new(
    'PONG',
    r'^:(?P<server>\S+) PONG (?P=server) :?(?P<data>.*)')

NEW_NICK = raw.new('NEW_NICK', r'^:(?P<nick>\S+) NICK :?(?P<new_nick>\S+)')

JOIN = raw.new('JOIN', r'^:(?P<mask>\S+) JOIN :?(?P<channel>\S+)')
PART = raw.new('PART',
               r'^:(?P<mask>\S+) PART (?P<channel>\S+)(\s+:(?P<data>.*)|$)')
QUIT = raw.new('QUIT',
               r'^:(?P<mask>\S+) QUIT(\s+:(?P<data>.*)|$)')

JOIN_PART_QUIT = raw.new(
    'JOIN_PART_QUIT',
    (r'^:(?P<mask>\S+) '
     r'(?P<event>JOIN|PART|QUIT)\s*:*(?P<channel>\S*)(\s+:(?P<data>.*)|$)'))

KICK = raw.new(
    'KICK',
    (r'^:(?P<mask>\S+) '
     r'(?P<event>KICK)\s+(?P<channel>\S+)\s*(?P<target>\S+)'
     r'(\s+:(?P<data>.*)|$)'))

MODE = raw.new(
    'MODE',
    (r'^:(?P<mask>\S+) (?P<event>MODE)\s+'
     r'(?P<target>\S+)\s+(?P<modes>\S+)(\s+(?P<data>.*)|$)'
     ))

MY_PRIVMSG = raw.new(
    'MY_PRIVMSG',
    (r'^:(?P<mask>\S+!\S+@\S+) (?P<event>(PRIVMSG|NOTICE)) '
        r'(?P<target>(#\S+|{nick})) :{nick}[:,\s]\s*'
        r'(?P<data>\S+.*)$'))

PRIVMSG = raw.new(
    'PRIVMSG',
    (r'^:(?P<mask>\S+!\S+@\S+) (?P<event>(PRIVMSG|NOTICE)) '
     r'(?P<target>\S+) :\s*(?P<data>\S+.*)$'))

CTCP = raw.new(
    'CTCP',
    ('^:(?P<mask>\S+!\S+@\S+) (?P<event>(PRIVMSG|NOTICE)) '
     '{nick} :\x01(?P<ctcp>\S+.*)\x01$'))

INVITE = raw.new(
    'INVITE',
    (r'^:(?P<mask>\S+!\S+@\S+) INVITE {nick} :?(?P<channel>\S+)$'))

TOPIC = raw.new(
    'TOPIC',
    (r'^:(?P<mask>\S+!\S+@\S+) TOPIC (?P<channel>\S+) :(?P<data>\S+.*)$'))

ERR_NICK = raw.new(
    'ERR_NICK',
    "^:(?P<srv>\S+) (?P<retcode>(432|433|436)) (?P<me>\S+) "
    "(?P<nick>\S+) :(?P<data>.*)")
