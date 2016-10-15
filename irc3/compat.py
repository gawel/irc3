# -*- coding: utf-8 -*-
import sys
import types

PY34 = bool(sys.version_info[0:2] >= (3, 4))
PY35 = bool(sys.version_info[0:2] >= (3, 5))


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
