# -*- coding: utf-8 -*-
from collections import defaultdict
import pprint
import re

_re_num = re.compile('\s(?P<num>\d+)\s+(?P<name>(RPL|ERR)_\w+)\s*(?P<_>.*)')
_re_mask = re.compile('^\s{24,25}(?P<_>("(<|:).*|\S.*"$))')


def main():
    print('Parsing rfc file...')
    item = None
    items = []

    out = open('irc3/_rfc.py', 'w')

    with open('irc3/rfc1459.txt') as fd:
        for line in fd:
            line = line.replace('<host> * <host>', '<host> * <host1>')
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
class retcode(int):
    name = None
    re = None

'''.lstrip())

    valids = set()
    for i, item in sorted(items):
        mask = item['mask']
        if mask:
            num = item['num']
            valids.add(i)
            out.write('\n')
            out.write('%(name)s = retcode(%(num)s)\n' % item)
            out.write('%(name)s.name = "%(name)s"\n' % item)
            mask = [s.strip('"\\ ') for s in mask]
            omask = ' '.join(mask)

            params = []

            def repl(v):
                v = v.lower()
                v = v.replace('nickname', 'nick')
                v = v.replace('nicks', 'nicknames')
                for c in '!@*':
                    v = v.replace(c, '')
                for c in '| ':
                    v = v.replace(c, '_')
                v = v.strip(' _')
                if v.endswith('_name'):
                    v = v[:-5]
                if v == 'client_ip_address_in_dot_form':
                    v = 'clientip'
                if v == 'integer':
                    for k in 'xyz':
                        if k not in params:
                            v = k
                            break
                if v == 'command':
                    v = 'cmd'
                if v == 'real':
                    v = 'realname'
                if v == 'name' and 'nick' not in params:
                    v = 'nick'
                if v == 'user':
                    if 'nick' not in params and num not in ('352',):
                        v = 'nick'
                    else:
                        v = 'username'
                return v

            def tsub(m):
                v = m.groupdict()['m'].strip('<>')
                v = repl(v)
                params.append(v)
                return '{%s}' % v

            if item['num'] == '303':
                omask = ':<nicknames>'
            elif item['num'] == '311':
                omask = omask.replace('*', '<m>')
            elif item['num'] == '319':
                omask = ':<channels>'
            elif item['num'] == '353':
                omask = '<m> <channel> :<nicknames>'

            tpl = _re_sub.sub(tsub, omask)
            for v in ((' %d ', '{days}'),
                      ('%d:%02d:%02d', '{hours}'),
                      (':%-8s %-9s %-8s', '{x} {y} {z}')):
                tpl = tpl.replace(*v)
            tpl_ = [':{c.srv} ' + item['num'] + ' {c.nick} ']
            if len(tpl) > 60:
                tpl_.extend([':' + s for s in tpl.split(':', 1)])
            else:
                tpl_.append(tpl)
            tpl = '\n    '.join([repr(v) for v in tpl_])

            params = []

            def msub(m):
                v = m.groupdict()['m'].strip('<>')
                v = repl(v)
                params.append(v)
                return '(?P<%s>\S+)' % v

            mask = _re_sub.sub(msub, omask)
            if '???? ' in mask:
                mask = mask.replace('???? ', r'\S+ ')
            if ' * ' in mask:
                mask = mask.replace(' * ', r' . ')
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
            out.write('%(name)s.tpl = (\n' % dict(item))
            out.write('    %s)\n' % tpl)
            out.write('%(name)s.params = %(p)s\n' % dict(item, p=params))

    out.write('\n')
    out.write('RETCODES = {\n')
    for i, item in sorted(items):
        if i in valids:
            out.write('    %(num)s: %(name)s,\n' % item)
    out.write('}\n')


if __name__ == '__main__':
    main()
