# -*- coding: utf-8 -*-
"""W36 review collector #2: roadmap tasks, dir listings, csv."""
import json, os, datetime, sqlite3

BASE = '/root/27-study'
today = datetime.date(2026, 9, 6)

def p(*a):
    print(*a)

p('=== ROADMAP tasks detail ===')
rm = json.load(open(BASE + '/状态数据/roadmap.json', encoding='utf-8'))
tasks = rm.get('tasks', [])
p('total tasks:', len(tasks))
ph = rm.get('phases', [])
for x in ph:
    p('phase:', x.get('id'), x.get('status'), x.get('date_range'))

# subject count by phase-3
for subj in ['408', '数学', '英语', '政治', '综合']:
    n = sum(1 for t in tasks if t.get('phase_id') == 'phase-3' and t.get('subject') == subj)
    p('phase-3 subject', subj, n)

archived = sum(1 for t in tasks if t.get('archived'))
p('archived tasks:', archived)

p('\n--- phase-3 tasks 2026-08-31..2026-09-13 (planned window) ---')
for t in sorted(tasks, key=lambda x: x.get('date', 'z')):
    d = t.get('date', '')
    if t.get('phase_id') == 'phase-3' and '2026-08-31' <= d <= '2026-09-13':
        print(t.get('id'), t.get('status'), d, t.get('subject'), '|', str(t.get('title'))[:44], '| minutes=', t.get('planned_minutes'), '| actual=', t.get('actual_minutes'), '| act_date=', t.get('actual_date'))

p('\n--- last task id / statuses of all non-archived ---')
from collections import Counter
c = Counter(t.get('status') for t in tasks if not t.get('archived'))
p(dict(c))
nonarch = [t for t in tasks if not t.get('archived')]
if nonarch:
    p('min/max id non-archived:', nonarch[0].get('id'), nonarch[-1].get('id'), 'count', len(nonarch))

p('\n--- tasks completed ever ---')
comp = [t for t in tasks if t.get('status') == 'completed']
p('completed count:', len(comp))
for t in comp[:40]:
    print(t.get('id'), t.get('date'), t.get('subject'), str(t.get('title'))[:30], 'actual_date=', t.get('actual_date'))

p('\n=== exam-study-log.csv ===')
try:
    print(open(BASE + '/每日记录/exam-study-log.csv', encoding='utf-8').read())
except Exception as e:
    p('ERR', repr(e))

for dname in ['/root/27-study/错题本', '/root/27-study/总结/每日', '/root/27-study/总结/阶段', '/root/27-study/每日记录']:
    p('\n=== dir', dname, '===')
    try:
        items = os.listdir(dname)
        p('entries:', items if items else '(empty)')
    except Exception as e:
        p('ERR', repr(e))

p('\n=== system-state day math ===')
d0 = datetime.date(2026, 7, 31)
p('days since 7/31:', (today - d0).days, '| 1-indexed day:', (today - d0).days + 1)

p('\n=== sqlite: state.db tables ===')
for db in ['/root/.hermes/profiles/408-study/state.db', '/root/.hermes/profiles/408-study/cron/executions.db']:
    p('\n---', db)
    try:
        con = sqlite3.connect(db)
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabs = [r[0] for r in cur.fetchall()]
        p('tables:', tabs)
        con.close()
    except Exception as e:
        p('ERR', repr(e))
