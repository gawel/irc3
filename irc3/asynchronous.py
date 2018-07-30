# -*- coding: utf-8 -*-
from .compat import asyncio
import functools
import re


class event:

    iotype = 'in'
    iscoroutine = True

    def __init__(self, **kwargs):
        self.meta = kwargs.get('meta')
        regexp = self.meta['match'].format(**kwargs)
        self.regexp = regexp
        regexp = getattr(self.regexp, 're', self.regexp)
        self.cregexp = re.compile(regexp).match

    def compile(self, *args, **kwargs):
        return self.cregexp

    def __repr__(self):
        s = getattr(self.regexp, 'name', self.regexp)
        name = self.__class__.__name__
        return '<temp_event {0} {1}>'.format(name, s)

    def __call__(self, callback):
        self.callback = asyncio.coroutine(functools.partial(callback, self))
        return self


def default_result_processor(self, results=None, **value):  # pragma: no cover
    value['results'] = results
    if len(results) == 1:
        value.update(results[0])
    return value


def async_events(context, events, send_line=None,
                 process_results=default_result_processor,
                 timeout=30, **params):

    loop = context.loop
    task = asyncio.Future(loop=loop)  # async result
    results = []  # store events results
    events_ = []  # reference registered events

    # async timeout
    timeout = asyncio.ensure_future(
        asyncio.sleep(timeout, loop=loop), loop=loop)

    def end(t=None):
        """t can be a future (timeout done) or False (result success)"""
        if not task.done():
            # cancel timeout if needed
            if t is False:
                timeout.cancel()
            # detach events
            context.detach_events(*events_)
            # clean refs
            events_[:] = []
            # set results
            task.set_result(process_results(results=results, timeout=bool(t)))

    # end on timeout
    timeout.add_done_callback(end)

    def callback(e, **kw):
        """common callback for all events"""
        results.append(kw)
        if e.meta.get('multi') is not True:
            context.detach_events(e)
            events_.remove(e)
        if e.meta.get('final') is True:
            # end on success
            end(False)

    events_.extend([event(meta=kw, **params)(callback) for kw in events])

    context.attach_events(*events_, insert=True)

    if send_line:
        context.send_line(send_line.format(**params))

    return task


class AsyncEvents:
    """Asynchronious events"""

    timeout = 30
    send_line = None
    events = []

    def __init__(self, context):
        self.context = context

    def process_results(self, results=None, **value):  # pragma: no cover
        """Process results.
        results is a list of dict catched during event.
        value is a dict containing some metadata (like timeout=(True/False).
        """
        return default_result_processor(results=results, **value)

    def __call__(self, **kwargs):
        """Register events; and callbacks then return a `asyncio.Future`.
        Events regexp are compiled with `params`"""
        kwargs.setdefault('timeout', self.timeout)
        kwargs.setdefault('send_line', self.send_line)
        kwargs['process_results'] = self.process_results
        return async_events(self.context, self.events, **kwargs)
