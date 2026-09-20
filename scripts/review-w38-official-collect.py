# -*- coding: utf-8 -*-
"""W38 正式版复盘 · 采集 #1：roadmap 窗口/逾期/phase/408 编号（只读）"""
import json
from collections import Counter

RM = '/root/27-study/状态数据/roadmap.json'
rm = json.load(open(RM, encoding='utf-8'))
ts = rm['tasks']
today = '2026-09-20'

print('=== 总览 ===')
print('total tasks:', len(ts))
print('status:', dict(Counter(t.get('status') for t in ts)))
print('archived(flag):', sum(1 for t in ts if t.get('archived')))

print('\n=== 9/14-9/20 任务（W38 窗口）===')
win = [t for t in ts if '2026-09-14' <= t.get('date', '') <= today]
print('count =', len(win))
for t in sorted(win, key=lambda x: (x['date'], x['id'])):
    print('  %s %s [%s] %s | %s min | %s' % (
        t['id'], t['date'], t.get('status'), (t.get('title') or '')[:40],
        t.get('estimated_minutes'), 'ARCHIVED' if t.get('archived') else ''))

print('\n=== 每日分钟数（TASKS 口径，第5列=脚本输出，此处用 estimated_minutes）===')
for d in sorted(set(t['date'] for t in win)):
    ds = [t for t in win if t['date'] == d]
    print('  %s n=%d archived=%d' % (d, len(ds), sum(1 for t in ds if t.get('archived'))))

print('\n=== 逾期（date<2026-09-20, 未完成, 排除 archived）===')
od = [t for t in ts if t.get('date', '') < today and t.get('status') != 'completed' and not t.get('archived')]
print('count =', len(od))
if od:
    print('最早 =', min(t['date'] for t in od), ' 最新 =', max(t['date'] for t in od))
    print('按科目:', dict(Counter(t.get('subject') for t in od)))
    print('按 phase:', dict(Counter(t.get('phase_id') for t in od)))

print('\n=== 归档任务 ===')
ar = [t for t in ts if t.get('archived')]
print('count =', len(ar), dict(Counter(t.get('phase_id') for t in ar)))

print('\n=== 未来任务（>2026-09-20）===')
fu = [t for t in ts if t.get('date', '') > today and not t.get('archived')]
print('count =', len(fu))
if fu:
    print('范围:', min(t['date'] for t in fu), '..', max(t['date'] for t in fu))

print('\n=== 9/18-9/27 逐日任务 ===')
for d in ['2026-09-18', '2026-09-19', '2026-09-20', '2026-09-21', '2026-09-22',
          '2026-09-23', '2026-09-24', '2026-09-25', '2026-09-26', '2026-09-27']:
    ds = [t for t in ts if t.get('date') == d]
    print('  %s n=%d | %s' % (d, len(ds), ' ; '.join('%s[%s]' % (t['id'], t.get('status')) for t in ds)))

print('\n=== 408 任务全链（非归档）===')
p408 = sorted([t for t in ts if t.get('subject') == '408' and not t.get('archived')], key=lambda x: x['id'])
print('count =', len(p408))
for t in p408[:4]:
    print('  head', t['id'], t['date'], (t.get('title') or '')[:50])
print('  ...')
for t in p408[-4:]:
    print('  tail', t['id'], t['date'], (t.get('title') or '')[:50])

print('\n=== phase 状态 ===')
for p in rm['phases']:
    print('  ', p.get('id'), p.get('title'), p.get('status'), p.get('date_range'))

print('\n=== metadata ===')
print(json.dumps(rm.get('metadata'), ensure_ascii=False)[:900])
