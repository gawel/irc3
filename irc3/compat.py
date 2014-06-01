# -*- coding: utf-8 -*-
import sys
PY3 = bool(sys.version_info[0] == 3)

if PY3:  # pragma: no cover
    text_type = str
    string_types = (bytes, str)
else:  # pragma: no cover
    text_type = unicode
    string_types = basestring

try:  # pragma: no cover
    import asyncio
    from asyncio.queues import Queue
    from asyncio.queues import QueueFull  # NOQA
except ImportError:  # pragma: no cover
    import trollius as asyncio  # NOQA
    from trollius.queues import Queue  # NOQA
    from trollius.queues import QueueFull  # NOQA
