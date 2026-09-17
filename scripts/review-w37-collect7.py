# -*- coding: utf-8 -*-
"""W37 collector #7: 本周任务清单 + 逾期口径统计（只读）。"""
import json
from collections import Counter

rm = json.load(open('/root/27-study/状态数据/roadmap.json', encoding='utf-8'))
ts = rm['tasks']

print('=== 9/7-9/13 任务（W37 窗口）===')
for t in sorted([x for x in ts if x.get('date', '') >= '2026-09-07' and x.get('date', '') <= '2026-09-13'], key=lambda x: x['id']):
    print('  %s %s [%s] %s %s | %smin | %s' % (
        t['id'], t['date'], t.get('subject'), t.get('status'), (t.get('title') or '')[:36],
        t.get('estimated_minutes'), 'archived' if t.get('archived') else ''))

print('\n=== 逾期统计（date<2026-09-13, 未完成, 排除 archived）===')
od = [t for t in ts if t.get('date', '') < '2026-09-13' and t.get('status') != 'completed' and not t.get('archived')]
print('  count =', len(od))
print('  最早 =', min(t['date'] for t in od), ' 最新 =', max(t['date'] for t in od))
print('  按科目:', Counter(t.get('subject') for t in od))
print('  按 phase:', Counter(t.get('phase_id') for t in od))

print('\n=== 当日+未来（>=2026-09-13）===')
fu = [t for t in ts if t.get('date', '') >= '2026-09-13' and not t.get('archived')]
print('  count =', len(fu), ' 范围:', min(t['date'] for t in fu), '..', max(t['date'] for t in fu))

print('\n=== 408 任务编号连续性（explicit 校准集）===')
for t in sorted([x for x in ts if x.get('subject') == '408' and not x.get('archived')], key=lambda x: x['id'])[:6]:
    print('  ', t['id'], t['date'], t.get('title'))
print('   ... 最后一个 408 任务:')
last = sorted([x for x in ts if x.get('subject') == '408' and not x.get('archived')], key=lambda x: x['id'])[-1]
print('  ', last['id'], last['date'], last.get('title'))

print('\n=== phase 状态 ===')
for p in rm['phases']:
    print('  ', p.get('id'), p.get('title'), p.get('status'), p.get('date_range'))

print('\n=== roadmap metadata ===')
print('  ', json.dumps(rm['metadata'], ensure_ascii=False)[:600])
