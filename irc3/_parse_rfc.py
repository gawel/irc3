# -*- coding: utf-8 -*-
from collections import defaultdict
import pprint
import re

_re_num = re.compile('\s(?P<num>\d+)\s+(?P<name>(RPL|ERR)_\w+)\s*(?P<_>.*)')
_re_mask = re.compile('^\s{24,25}(?P<_>("(<|:).*|\S.*"$))')


def main():
    item = None
    items = []

    out = open('irc3/_rfc.py', 'w')

    with open('irc3/rfc1459.txt') as fd:
        for line in fd:
            line = line.replace('<# visible>', '<visible>')
            line = line.replace('<H|G>[*][@|+]', '<modes>')
            line = line.replace('<nick!user|*!*>@<host|server>', '<mask>')
            match = _re_num.search(line)
            if match is not None:
                if item:
                    items.append((int(item['num']), item))
                item = defaultdict(list)
                match = match.groupdict()
                if '_' in match:
                    match.pop('_')
                item.update(match)
            match = _re_mask.search(line)
            if match is not None:
                item['mask'].append(match.groupdict()['_'])

    _re_sub = re.compile('(?P<m><[^>]+>)')

    out.write('''
from __future__ import unicode_literals


class retcode(int):
    name = None
    re = None
''')

    valids = set()
    for i, item in sorted(items):
        mask = item['mask']
        if mask:
            valids.add(i)
            out.write('\n')
            out.write('%(name)s = retcode(%(num)s)\n' % item)
            out.write('%(name)s.name = "%(name)s"\n' % item)
            mask = [s.strip('"\\ ') for s in mask]
            mask = ' '.join(mask)

            params = []

            def sub(m):
                v = m.groupdict()['m'].strip('<>')
                v = v.lower()
                v = v.replace('nickname', 'nick')
                for c in '!@*':
                    v = v.replace(c, '')
                for c in '| ':
                    v = v.replace(c, '_')
                v = v.strip(' _')
                if v.endswith('_name'):
                    v = v[:-5]
                if v == 'client_ip_address_in_dot_form':
                    v = 'clientip'
                params.append(v)
                return '(?P<%s>\S+)' % v

            mask = _re_sub.sub(sub, mask)
            if ':' in mask:
                mask = mask.split(':', 1)[0]
                mask += ':(?P<data>.*)'
            mask = '(?P<srv>\S+) ' + str(i) + ' (?P<me>\S+) "\n    "' + mask
            mask = mask.replace(
                ' (?P<server>\S+)',
                ' "\n    "(?P<server>\S+)')
            mask = mask.replace(
                ' (?P<sent_messages>\S+)',
                ' "\n    "(?P<sent_messages>\S+)')
            item['mask'] = mask
            params = [p for p in params if '<%s>' % p in mask]
            if '<data>' in mask and 'data' not in params:
                params.append('data')
            out.write('%(name)s.re = (\n    "^:%(mask)s")\n' % item)
            params = pprint.pformat(
                ['srv', 'me'] + params, width=60, indent=4)
            if len(params) > 60:
                params = params.replace('[', '[\n ')
            out.write('%(name)s.params = %(p)s\n' % dict(item, p=params))

    out.write('\n')
    out.write('RETCODES = {\n')
    for i, item in sorted(items):
        if i in valids:
            out.write('    %(num)s: %(name)s,\n' % item)
    out.write('}\n')
