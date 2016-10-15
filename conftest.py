# -*- coding: utf-8 -*-
from irc3 import testing
import pytest
import sys
import os

try:
    from redis.exceptions import ConnectionError
    from redis.client import StrictRedis
    StrictRedis().flushdb()
except (ImportError, ConnectionError):
    import re
    req_redis = re.compile(".*#[^#]*\s*require?\s*redis\s*$", re.IGNORECASE)

    def pytest_runtest_setup(item):
        if getattr(item, 'dtest', None):
            if any(req_redis.match(e.source) for e in item.dtest.examples):
                pytest.skip("No redis server is running")

dirname = os.path.dirname(__file__)
sys.path.append(os.path.join(dirname, 'examples'))


@pytest.fixture(scope="function")
def cls_event_loop(request, event_loop):
    request.cls.loop = event_loop
    request.cls.config['loop'] = event_loop
    yield
    request.cls.config.pop('loop')


@pytest.fixture(scope="function")
def irc3_bot_factory(request, event_loop):
    def _bot(**config):
        config['loop'] = event_loop
        _b['b'] = testing.IrcBot(**config)
        return _b['b']
    _b = {}
    yield _bot
    _b['b'].SIGINT()
