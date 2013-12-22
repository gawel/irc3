# -*- coding: utf-8 -*-
from ._rfc import *  # NOQA


class raw(str):
    name = None
    re = None

    @classmethod
    def new(cls, name, regexp):
        r = cls(name)
        r.name = name
        r.re = regexp
        return r

PING = raw.new('PING', r'PING :(?P<data>.*)')
NEW_NICK = raw.new('NEW_NICK', r':(?P<nick>\S+) NICK (?P<new_nick>\S+)')
JOIN = raw.new('JOIN', r':(?P<mask>\S+) JOIN (?P<channel>\S+)')
PART = raw.new('PART',
               r':(?P<mask>\S+) PART (?P<channel>\S+)(\s+:(?P<data>.*)|$)')
QUIT = raw.new('QUIT',
               r':(?P<mask>\S+) QUIT(\s+:(?P<data>.*)|$)')

JOIN_PART_QUIT = raw.new(
    'JOIN_PART_QUIT',
    (r':(?P<mask>\S+) '
     r'(?P<event>JOIN|PART|QUIT)\s*(?P<channel>\S*)(\s+:(?P<data>.*)|$)'))

MY_PRIVMSG = raw.new(
    'MY_PRIVMSG',
    (r':(?P<mask>\S+!\S+@\S+) (?P<event>(PRIVMSG|NOTICE)) '
        r'(?P<target>(#\S+|%(nick)s)) :%(nick)s[:,\s]\s*'
        r'(?P<data>\S+.*)$'))

PRIVMSG = raw.new(
    'PRIVMSG',
    (r':(?P<mask>\S+!\S+@\S+) (?P<event>(PRIVMSG|NOTICE)) '
        r'((?P<target>\S+) :\s*(?P<data>\S+.*)$'))

ERR_NICK = raw.new(
    'ERR_NICK',
    ":(?P<srv>\S+) (?P<retcode>(432|433|436)) (?P<me>\S+) "
    "(?P<nick>\S+) :(?P<data>.*)")
