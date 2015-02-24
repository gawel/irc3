# -*- coding: utf-8 -*-
from . import rfc
from . import template
import os


def render_attrs(title, attrs, out):
    out.write(title + '\n')
    out.write(len(title)*'=' + '\n')
    out.write('\n')
    for attr in attrs:
        name = attr.name
        title = name
        if isinstance(attr, int):
            title = '%s - %s' % (attr, title)
        out.write(title + '\n')
        out.write(len(title)*'-' + '\n\n')
        if hasattr(attr, 'tpl'):
            out.write('Format ``%s``\n\n' % attr.tpl.replace('{c.', '{'))
        out.write('Match ``%s``\n\n' % attr.re)
        out.write('Example:\n\n')
        out.write('.. code-block:: python\n\n')
        out.write('    @irc3.event(rfc.%s)\n' % name)
        params = getattr(attr, 'params', [])
        if params:
            params = '=None, '.join(params)
            out.write('    def myevent(bot, %s=None):\n' % params)
        else:
            out.write('    def myevent(bot):\n' % params)
        out.write('        # do something\n')
        out.write('\n')


def main():
    print('Generate docs...')

    attrs = [getattr(rfc, attr) for attr in dir(rfc)
             if attr.isupper() and attr not in ('RETCODES',)]
    repls = [attr for attr in attrs if attr.name.startswith('RPL_')]
    errs = [attr for attr in attrs if attr.name.startswith('ERR_')]
    misc = [attr for attr in attrs
            if not attr.name.startswith(('ERR_', 'RPL_'))]
    out = open('docs/rfc.rst', 'w')
    out.write('========================\n')
    out.write(':mod:`irc3.rfc` RFC1459\n')
    out.write('========================\n\n')
    render_attrs('Replies (REPL)', repls, out)
    render_attrs('Errors (ERR)', errs, out)
    render_attrs('Misc', misc, out)

    try:
        os.makedirs('docs/plugins')
    except OSError:
        pass

    for filename in os.listdir('irc3/plugins'):
        if filename.startswith('_'):
            continue
        if not filename.endswith('.py'):
            continue
        filename = filename.replace('.py', '')
        modname = 'irc3.plugins.%s' % filename
        out = open('docs/plugins/' + filename + '.rst', 'w')
        out.write('.. automodule:: ' + modname + '\n')
        out.write('\n')

    template.main(nick='mybot',
                  dest=os.path.join(os.getcwd(), 'examples'))


if __name__ == '__main__':
    main()
