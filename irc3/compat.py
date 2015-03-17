# -*- coding: utf-8 -*-
import sys
import types
PY3 = bool(sys.version_info[0] == 3)
PY34 = bool(sys.version_info[0:2] >= (3, 4))
PY35 = bool(sys.version_info[0:2] >= (3, 5))


def u(value):
    if not PY3:  # pragma: no cover
        return value.decode('utf8')
    return value


if PY3:  # pragma: no cover
    from urllib.request import urlopen
    text_type = str
    string_types = (bytes, str)
    def isclass(o):
        return isinstance(o, type)
else:  # pragma: no cover
    from urllib2 import urlopen
    text_type = unicode
    string_types = basestring
    def isclass(o):
        return isinstance(o, (type, types.ClassType))

import configparser  # NOQA

try:  # pragma: no cover
    from importlib import reload as reload_module
except ImportError:  # pragma: no cover
    from imp import reload as reload_module  # NOQA

try:  # pragma: no cover
    import asyncio
    from asyncio.queues import Queue
    from asyncio.queues import QueueFull  # NOQA
except ImportError:  # pragma: no cover
    import trollius as asyncio  # NOQA
    from trollius.queues import Queue  # NOQA
    from trollius.queues import QueueFull  # NOQA
