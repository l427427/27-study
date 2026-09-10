# -*- coding: utf-8 -*-
"""W36 review data collector. Prints key study data for weekly review."""
import json, os, datetime

BASE = '/root/27-study'

def p(*a):
    print(*a)

p('=== NOW ===')
now = datetime.datetime.now()
p('now:', now.isoformat(), '| isocalendar:', now.isocalendar())
p('weekday(0=Mon):', now.weekday())

p('\n=== CHANGELOG tail ===')
try:
    lines = open(BASE + '/状态数据/roadmap-changelog.md', encoding='utf-8').read().splitlines()
    p('total lines:', len(lines))
    p('\n'.join(lines[-80:]))
except Exception as e:
    p('ERR changelog:', repr(e))

def show_md(name, path, cap=6000):
    p('\n=== %s ===' % name)
    try:
        s = open(path, encoding='utf-8').read()
        p('len:', len(s))
        print(s[:cap])
        if len(s) > cap:
            p('...[truncated, total %d chars]' % len(s))
    except Exception as e:
        p('ERR', name, repr(e))

show_md('W35 weekly', BASE + '/总结/每周/2026-W35.md', 6000)
show_md('EXISTING W36 weekly', BASE + '/总结/每周/2026-W36.md', 25000)

p('\n=== MASTERY ===')
try:
    m = json.load(open(BASE + '/状态数据/mastery.json', encoding='utf-8'))
    print(json.dumps(m, ensure_ascii=False, indent=1)[:4000])
except Exception as e:
    p('ERR mastery:', repr(e))

p('\n=== DASHBOARD 状态数据/dashboard-data.json (top-level) ===')
try:
    d = json.load(open(BASE + '/状态数据/dashboard-data.json', encoding='utf-8'))
    for k, v in d.items():
        if isinstance(v, list):
            p('key list:', k, 'len', len(v))
        elif isinstance(v, dict):
            p('key dict:', k, '->', json.dumps(v, ensure_ascii=False)[:400])
        else:
            p('key:', k, '=', v)
except Exception as e:
    p('ERR dashboard:', repr(e))

p('\n=== ROADMAP structure ===')
try:
    rm = json.load(open(BASE + '/状态数据/roadmap.json', encoding='utf-8'))
    print('top keys:', list(rm.keys()) if isinstance(rm, dict) else type(rm))
    s = json.dumps(rm, ensure_ascii=False)
    p('raw len:', len(s))
    print('raw head:', s[:600])
except Exception as e:
    p('ERR roadmap:', repr(e))
