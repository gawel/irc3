# -*- coding: utf-8 -*-
from functools import partial
from .compat import asyncio
from .dec import event


class async_event(event):

    def __init__(self, regexp, results, future=None, **config):
        self.config = config
        self.results = results
        self.future = future
        super(async_event, self).__init__(regexp)
        self.compile()

    def compile(self, *args, **kwargs):
        super(async_event, self).compile(self.config)

    def async_callback(self, kw):
        self.results.append(kw)
        if self.future:
            self.future.set_result(self.results)


class AsyncEvents(object):
    """Asynchronious events"""

    timeout = 30

    events = []
    extra_events = []

    def __init__(self, context, events=None, extra_events=None, timeout=None):
        self.context = context
        if events:
            self.events = events
        if extra_events:
            self.events = extra_events

    def timeout_callback(self, events, future, results, config):
        self.context.log.warn('%s(**{%r}) return %r after timeout',
                              self.__class__.__name__, results, config)
        self.context.detach_events(*events)
        future.set_result(self.process_results(results=results, timeout=True))

    def done_callback(self, events, future, timeout, result):
        timeout.cancel()
        self.context.detach_events(*events)
        future.set_result(self.process_results(results=result.result(),
                                               timeout=False))

    def process_results(self, results=None, **value):
        """Process results.
        result is a list of dict catched during event.
        value is a dict containing some metadata (like timeout=(True/False).
        """
        value['results'] = results
        if len(results) == 1:
            value.update(results[0])
        return value

    def __call__(self, timeout=None, **config):
        """Register events; and callbacks then return a `asyncio.Future`.
        Events regexp are compiled with `config`"""
        results = []

        events = [
            async_event(e, results, future=None, **config)
            for e in self.extra_events]

        result = asyncio.Future()
        events.extend([
            async_event(e, results, future=result, **config)
            for e in self.events])

        task = asyncio.Future()

        if timeout is None:
            timeout = self.timeout
        timeout = self.context.loop.call_later(
            timeout,
            partial(self.timeout_callback, events, task, results, config))

        result.add_done_callback(
            partial(self.done_callback, events, task, timeout))

        self.context.attach_events(*events, insert=True)

        return task
