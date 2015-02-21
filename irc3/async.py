# -*- coding: utf-8 -*-
from .compat import asyncio
from .dec import event


class async_event(event):

    def __init__(self, **kwargs):
        self.meta = kwargs.get('meta')
        super(async_event, self).__init__(self.meta['match'],
                                          callback=kwargs.pop('callback'))
        super(async_event, self).compile(kwargs)

    def compile(self, *args, **kwargs):
        # we don't need to recompile. params will never change
        pass

    def async_callback(self, kw):
        self.callback(self, kw)


def default_result_processor(self, results=None, **value):
    value['results'] = results
    if len(results) == 1:
        value.update(results[0])
    return value


def async_events(context, events, send_line=None,
                 process_results=default_result_processor,
                 timeout=30, **params):

    task = asyncio.Future()  # async result
    results = []  # store events results
    events_ = []  # reference registered events

    def timeout_callback():
        """occurs when no final=True event is found"""
        context.detach_events(*events_)
        task.set_result(process_results(results=results, timeout=True))

    timeout = context.loop.call_later(timeout, timeout_callback)

    def callback(e, kw):
        """common callback for all events"""
        results.append(kw)
        if e.meta.get('multi') is False:
            context.detach_events(e)
            events_.remove(e)
        if e.meta.get('final') is True:
            timeout.cancel()
            task.set_result(process_results(results, timeout=False))
            # detach events as soon as possible
            context.detach_events(*events_)
            # empty in place (still use ref)
            events_[:] = []

    events_.extend([
        async_event(meta=kw, callback=callback, **params)
        for kw in events])

    context.attach_events(*events_, insert=True)

    if send_line:
        context.send_line(send_line.format(**params))

    return task


class AsyncEvents(object):
    """Asynchronious events"""

    timeout = 30
    send_line = None
    events = []

    def __init__(self, context):
        self.context = context

    def process_results(self, results=None, **value):
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
