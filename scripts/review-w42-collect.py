# -*- coding: utf-8 -*-
"""W42 周复盘采集: roadmap 结构 / phase / 本周窗口任务 / changelog 尾部 / dashboard 口径"""
import json, os, subprocess
from datetime import date, datetime

ROOT = '/root/27-study'
today = date(2026, 10, 18)
wk_start = date(2026, 10, 12)

def load(p):
    with open(os.path.join(ROOT, p), encoding='utf-8') as f:
        return json.load(f)

rm = load('状态数据/roadmap.json')
st = load('状态数据/system-state.json')
db = load('状态数据/dashboard-data.json')

tasks = rm['tasks']
print('=== A. roadmap 顶层 ===')
print('roadmap_version:', rm.get('roadmap_version'), '| title:', rm.get('title'))
print('tasks_total:', len(tasks), '| pending:', sum(1 for t in tasks if t.get('status') != 'completed' and not t.get('archived')),
      '| archived:', sum(1 for t in tasks if t.get('archived')),
      '| completed:', sum(1 for t in tasks if t.get('status') == 'completed'))
ds = sorted(t['date'] for t in tasks if not t.get('archived'))
print('date_range:', ds[0], '..', ds[-1])
print('tasks today(10-18):', len([t for t in tasks if t.get('date') == '2026-10-18']))
print('tasks >= 2026-10-01:', len([t for t in tasks if t.get('date') >= '2026-10-01']))

print('\n=== B. phases ===')
for ph in rm.get('phases', []):
    print(' ', ph.get('phase_id') or ph.get('id'), '|', ph.get('status'), '|', ph.get('date_range') or (ph.get('start_date'), ph.get('end_date')), '|', str(ph.get('title'))[:40])

print('\n=== C. 本周窗口任务 (10-12..10-18) ===')
wk = [t for t in tasks if wk_start.isoformat() <= t.get('date', '') <= today.isoformat()]
print('count:', len(wk))
for t in wk:
    print(' ', t['id'], t['date'], t.get('status'), t.get('archived'), str(t.get('title'))[:50])

print('\n=== D. 末 10 个任务（按日期） ===')
for t in sorted(tasks, key=lambda x: (x['date'], x['id']))[-10:]:
    print(' ', t['id'], t['date'], t.get('status'), 'archived=%s' % t.get('archived'), str(t.get('title'))[:45])

print('\n=== E. 按科目统计（独立重数，排除 archived） ===')
from collections import Counter
c = Counter()
for t in tasks:
    if t.get('archived'):
        continue
    c[t.get('subject', '(none)')] += 1
print(' ', dict(c), '| sum =', sum(c.values()))

print('\n=== F. dashboard-data.json 顶层键与口径 ===')
print(' keys:', sorted(db.keys()))
for k in ('total_tasks', 'completed', 'pending', 'overdue', 'overdue_tasks', 'current_day', 'cycle_percent', 'generated_at', 'updated_at'):
    if k in db:
        print('  %s = %r' % (k, db[k]))
if 'subjects' in db:
    print('  subjects =', db['subjects'])
if 'today_tasks' in db:
    print('  today_tasks n =', len(db['today_tasks']))

print('\n=== G. system-state ===')
print(' current_status:', st['current_status'], '| current_day:', st['current_project']['current_day'],
      '| today.date:', st['today_session']['date'], '| updated_at:', st['updated_at'])

print('\n=== H. 文件 mtime ===')
for p in ('状态数据/roadmap.json', '状态数据/system-state.json', '状态数据/dashboard-data.json', '总结/每周/2026-W41.md'):
    fp = os.path.join(ROOT, p)
    print(' ', p, datetime.fromtimestamp(os.path.getmtime(fp)).strftime('%Y-%m-%d %H:%M'))
