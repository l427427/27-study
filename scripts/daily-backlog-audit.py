#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""每日 09:00 提醒 job 的 backlog 巡检（只读，不改任何数据）。

判据三件套：
  ① date < 今天 且 status != completed 且无 archived 的积压任务数 + 最早日期
  ② 今日任务清单（roadmap 里 date == today）
  ③ 每日记录/ 与 总结/每日/ 文件新鲜度 + system-state.today_session.date 与真实日期差

用法: cd /root/27-study/scripts && python3 -u daily-backlog-audit.py 2>&1 | head -40
"""
import json, os, datetime

ROOT = '/root/27-study'
today = datetime.datetime.now().strftime('%Y-%m-%d')

rm = json.load(open(os.path.join(ROOT, '状态数据', 'roadmap.json'), encoding='utf-8'))
tasks = rm.get('tasks', [])

backlog = [t for t in tasks
           if t.get('date') and t['date'] < today
           and t.get('status') != 'completed' and not t.get('archived')]
done_log = [t for t in tasks if t.get('status') == 'completed']

print('today=%s  tasks_total=%d' % (today, len(tasks)))
print('backlog(pending,date<today,not archived)=%d  earliest=%s  latest=%s'
      % (len(backlog),
         min((t['date'] for t in backlog), default='-'),
         max((t['date'] for t in backlog), default='-')))
print('completed(all time)=%d' % len(done_log))

todays = sorted([t for t in tasks if t.get('date') == today], key=lambda x: x.get('id', ''))
print('--- today (%d) ---' % len(todays))
for t in todays:
    print('%s | %s | %s | min=%s | %s'
          % (t.get('id'), t.get('subject'), (t.get('title') or '')[:40],
             t.get('minutes'), t.get('status')))

st = json.load(open(os.path.join(ROOT, '状态数据', 'system-state.json'), encoding='utf-8'))
d0 = datetime.datetime.strptime(st['today_session']['date'], '%Y-%m-%d')
d1 = datetime.datetime.strptime(today, '%Y-%m-%d')
print('system-state.today_session.date=%s  drift_days=%d  current_day=%s'
      % (st['today_session']['date'], (d1 - d0).days, st['current_project'].get('current_day')))

for sub in ('每日记录', '总结/每日', '总结/每周'):
    p = os.path.join(ROOT, sub)
    if not os.path.isdir(p):
        print('%s: (missing dir)' % sub)
        continue
    fs = sorted(os.listdir(p))
    if fs:
        mt = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(p, fs[-1])))
        print('%s: n=%d  newest=%s (%s)' % (sub, len(fs), fs[-1], mt.strftime('%m-%d %H:%M')))
    else:
        print('%s: n=0 (empty)' % sub)
