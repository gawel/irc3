# -*- coding: utf-8 -*-
import sys
PY3 = bool(sys.version_info[0] == 3)


def u(value):
    if not PY3:  # pragma: no cover
        return value.decode('utf8')
    return value


if PY3:  # pragma: no cover
    text_type = str
    string_types = (bytes, str)
else:  # pragma: no cover
    text_type = unicode
    string_types = basestring

if PY3:  # pragma: no cover
    import configparser
else:  # pragma: no cover
    import ConfigParser as configparser  # NOQA

try:  # pragma: no cover
    import asyncio
    from asyncio.queues import Queue
    from asyncio.queues import QueueFull  # NOQA
except ImportError:  # pragma: no cover
    import trollius as asyncio  # NOQA
    from trollius.queues import Queue  # NOQA
    from trollius.queues import QueueFull  # NOQA
