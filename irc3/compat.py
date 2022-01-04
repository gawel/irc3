# -*- coding: utf-8 -*-
import sys
import types

PY34 = bool(sys.version_info[0:2] >= (3, 4))
PY35 = bool(sys.version_info[0:2] >= (3, 5))
PY37 = bool(sys.version_info[0:2] >= (3, 7))


try:  # pragma: no cover
    from importlib import reload as reload_module
except ImportError:  # pragma: no cover
    from imp import reload as reload_module  # NOQA

try:  # pragma: no cover
    import asyncio
    from asyncio.queues import Queue as BaseQueue
    from asyncio.queues import QueueFull  # NOQA
    from asyncio import sleep as _original_sleep
    from asyncio import wait as _original_wait
except ImportError:  # pragma: no cover
    import trollius as asyncio  # NOQA
    from trollius.queues import Queue  as BaseQueue # NOQA
    from trollius.queues import QueueFull  # NOQA
    from trollius import sleep as _original_sleep
    from trollius import wait as _original_wait


def __sleep(*args, **kwargs):
    if PY37 and "loop" in kwargs:
        del kwargs["loop"]
    return _original_sleep(*args, **kwargs)


def __wait(*args, **kwargs):
    if PY37 and "loop" in kwargs:
        del kwargs["loop"]
    return _original_wait(*args, **kwargs)


asyncio.sleep = __sleep
asyncio.wait = __wait

class Queue(BaseQueue):
    def __init__(self, *args, **kwargs):
        if PY37 and "loop" in kwargs:
            del kwargs["loop"]

        super().__init__(*args, **kwargs)
