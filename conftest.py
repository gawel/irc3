# -*- coding: utf-8 -*-
import sys
import os

try:
    from redis.exceptions import ConnectionError
    from redis.client import StrictRedis
    StrictRedis().flushdb()
except (ImportError, ConnectionError):
    import pytest
    import re
    req_redis = re.compile(".*#[^#]*\s*require?\s*redis\s*$", re.IGNORECASE)

    def pytest_runtest_setup(item):
        if getattr(item, 'dtest', None):
            if any(req_redis.match(e.source) for e in item.dtest.examples):
                pytest.skip("No redis server is running")

dirname = os.path.dirname(__file__)
sys.path.append(os.path.join(dirname, 'examples'))
