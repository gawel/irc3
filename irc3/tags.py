# -*- coding: utf-8 -*-
'''
Module offering 2 functions, encode() and decode(), to transcode between
IRCv3.2 tags and python dictionaries.
'''
import re
import random
import string


_escapes = (
    ("\\", "\\\\"),
    (";",  r"\:"),
    (" ",  r"\s"),
    ("\r", r"\r"),
    ("\n", r"\n"),
)

# make the possibility of the substitute actually appearing in the text
# negligible. Even for targeted attacks
_substitute = (";TEMP:%s;" %
               ''.join(random.choice(string.ascii_letters) for i in range(20)))
_unescapes = (
    ("\\\\", _substitute),
    (r"\:", ";"),
    (r"\s", " "),
    (r"\r", "\r"),
    (r"\n", "\n"),
    (_substitute, "\\"),
)

# valid tag-keys must contain of alphanumerics and hyphens only.
# for vendor-tagnames: TLD with slash appended
_valid_key = re.compile("^([\w.-]+/)?[\w-]+$")

# valid escaped tag-values must not contain
# NUL, CR, LF, semicolons or spaces
_valid_escaped_value = re.compile("^[^ ;\n\r\0]*$")


def _unescape(string):
    for a, b in _unescapes:
        string = string.replace(a, b)
    return string


def _escape(string):
    for a, b in _escapes:
        string = string.replace(a, b)
    return string


def encode(tags):
    '''Encodes a dictionary of tags to fit into an IRC-message.
    See IRC Message Tags: http://ircv3.net/specs/core/message-tags-3.2.html

    >>> from collections import OrderedDict
    >>> encode({'key': 'value'})
    'key=value'

    >>> d = {'aaa': 'bbb', 'ccc': None, 'example.com/ddd': 'eee'}
    >>> d_ordered = OrderedDict(sorted(d.items(), key=lambda t: t[0]))
    >>> encode(d_ordered)
    'aaa=bbb;ccc;example.com/ddd=eee'

    >>> d = {'key': 'value;with special\\\\characters', 'key2': 'with=equals'}
    >>> d_ordered = OrderedDict(sorted(d.items(), key=lambda t: t[0]))
    >>> print(encode(d_ordered))
    key=value\\:with\\sspecial\\\characters;key2=with=equals

    >>> print(encode({'key': r'\\something'}))
    key=\\\\something

    '''
    tagstrings = []
    for key, value in tags.items():
        if not _valid_key.match(key):
            raise ValueError("dictionary key is invalid as tag key: " + key)
        # if no value, just append the key
        if value:
            tagstrings.append(key + "=" + _escape(value))
        else:
            tagstrings.append(key)
    return ";".join(tagstrings)


def decode(tagstring):
    '''Decodes a tag-string from an IRC-message into a python dictionary.
    See IRC Message Tags: http://ircv3.net/specs/core/message-tags-3.2.html

    >>> from pprint import pprint
    >>> pprint(decode('key=value'))
    {'key': 'value'}

    >>> pprint(decode('aaa=bbb;ccc;example.com/ddd=eee'))
    {'aaa': 'bbb', 'ccc': None, 'example.com/ddd': 'eee'}

    >>> s = r'key=value\\:with\\sspecial\\\\characters;key2=with=equals'
    >>> pprint(decode(s))
    {'key': 'value;with special\\\\characters', 'key2': 'with=equals'}
    >>> print(decode(s)['key'])
    value;with special\\characters

    >>> print(decode(r'key=\\\\something')['key'])
    \\something

    '''
    if not tagstring:
        # None/empty = no tags
        return {}

    tags = {}

    for tag in tagstring.split(";"):
        # value is either everything after "=", or None
        key, value = (tag.split("=", 1) + [None])[:2]
        if not _valid_key.match(key):
            raise ValueError("invalid tag key: " + key)
        if value:
            if not _valid_escaped_value.match(value):
                raise ValueError("invalid escaped tag value: " + value)
            value = _unescape(value)
        tags[key] = value

    return tags
