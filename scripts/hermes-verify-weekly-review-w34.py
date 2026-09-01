#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ad-hoc verification for 2026-W34 weekly-review data changes.
Checks: JSON validity, roadmap integrity (408 contiguity 6→52),
dashboard consistency vs roadmap (W34 口径: overdue excl. archived = 72),
system-state freshness (8/23, day23), task-reminder-data.py 数据源根治.
"""
import json, re, sys

BASE = '/root/27-study/状态数据/'
fails = []

def check(name, cond, detail=''):
    status = 'PASS' if cond else 'FAIL'
    print(f'[{status}] {name}' + (f' — {detail}' if detail else ''))
    if not cond:
        fails.append(name)

def load(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)

# ---- 1. JSON validity ----
for fn in ['system-state.json', 'roadmap.json', 'dashboard-data.json', 'mastery.json', 'exam-schedule.json']:
    try:
        load(BASE + fn)
        check(f'{fn} valid JSON', True)
    except Exception as e:
        check(f'{fn} valid JSON', False, str(e))

# ---- 2. roadmap integrity ----
rm = load(BASE + 'roadmap.json')
tasks = rm['tasks']
check('roadmap has 112 tasks', len(tasks) == 112, str(len(tasks)))
ids = [t['id'] for t in tasks]
check('task ids unique', len(set(ids)) == len(ids))
req_keys = {'id', 'title', 'date', 'subject', 'phase_id', 'status', 'estimated_minutes'}
missing = [t['id'] for t in tasks if not req_keys.issubset(t.keys())]
check('all tasks have required keys', not missing, str(missing[:5]))

phases = {p['id']: p for p in rm['phases']}
check('phase-1 closed', phases['phase-1']['status'] == 'closed', phases['phase-1']['status'])
check('phase-2 active', phases['phase-2']['status'] == 'active', phases['phase-2']['status'])
check('phase-2 goal ~52讲', '52讲' in phases['phase-2']['goal'])

def lec_range(title):
    m = re.search(r'第(\d+)-(\d+)讲', title)
    return (int(m.group(1)), int(m.group(2))) if m else None

calib = [t for t in tasks if t['id'] in
         {'t039','t045','t051','t056','t059','t062','t065','t068','t071','t074',
          't077','t080','t083','t086','t089','t092','t095','t098','t101','t104','t107','t111'}]
ranges = []
for t in sorted(calib, key=lambda x: int(x['id'][1:])):
    r = lec_range(t['title'])
    ranges.append(r)
    check(f"{t['id']} has 408 lecture range", r is not None, str(t['title']))
contig = True
prev_end = 5
for a, b in ranges:
    if a != prev_end + 1:
        contig = False
        break
    prev_end = b
check('408 lecture numbers contiguous from 6', contig, str(ranges))
check('408 ends at 51-52 (8/27)', ranges[-1] == (51, 52), str(ranges[-1]))
stale = [t['id'] for t in tasks if t.get('subject') == '408' and lec_range(t['title'])
         and lec_range(t['title'])[0] > 52]
check('no 408 task beyond lecture 52', not stale, str(stale))

# metadata.last_review
check('metadata.last_review updated to W34', '2026-08-23' in (rm['metadata'].get('last_review') or ''),
      str(rm['metadata'].get('last_review')))

# ---- 3. dashboard-data.json consistency vs roadmap ----
db = load(BASE + 'dashboard-data.json')
exp_keys = {'dashboard_version','generated_at','summary','progress','tasks','subjects','phases','recent_activities','status'}
check('dashboard schema keys intact', exp_keys.issubset(db.keys()))
check('dashboard total=112', db['tasks']['total_tasks'] == 112, str(db['tasks']['total_tasks']))
check('dashboard completed=0 (no fabricated completion)', db['tasks']['completed_tasks'] == 0)
check('dashboard pending=112', db['tasks']['pending_tasks'] == 112)
# overdue: excl. archived (W34 正确口径 = 72)
overdue_manual = sum(1 for t in tasks if t.get('date') and t['date'] < '2026-08-23'
                     and t.get('status') != 'completed' and not t.get('archived'))
check('dashboard overdue=72 (excl. archived, recount)', db['tasks']['overdue_tasks'] == overdue_manual == 72,
      f"dashboard={db['tasks']['overdue_tasks']}, recount={overdue_manual}")
check('dashboard current_day=23', db['progress']['current_day'] == 23, str(db['progress']['current_day']))
check('dashboard days_remaining=125', db['progress']['days_remaining'] == 125, str(db['progress']['days_remaining']))
check('dashboard phase-1 closed / phase-2 active',
      db['phases']['phase-1']['status'] == 'closed' and db['phases']['phase-2']['status'] == 'active')

subj = {}
for t in tasks:
    subj[t['subject']] = subj.get(t['subject'], 0) + 1
# 允许 dashboard 预置的 total=0 科目（如 政治:0，每小时刷新脚本会预置）
dsubj = {k: v['total_tasks'] for k, v in db['subjects'].items() if v['total_tasks'] > 0}
check('dashboard subject counts == roadmap counts (zero-total extras allowed)',
      subj == dsubj, f'{subj} vs {dsubj}')
check('subject counts sum to 112', sum(dsubj.values()) == 112, str(sum(dsubj.values())))

# ---- 4. system-state.json freshness ----
ss = load(BASE + 'system-state.json')
check('system-state current_day=23', ss['current_project']['current_day'] == 23, str(ss['current_project']['current_day']))
check('system-state today=8/23', ss['today_session']['date'] == '2026-08-23', ss['today_session']['date'])
check('system-state last_session 8/6 no_report',
      ss['last_session']['date'] == '2026-08-06' and ss['last_session']['status'] == 'no_report')

# ---- 5. changelog + weekly report ----
with open(BASE + 'roadmap-changelog.md', encoding='utf-8') as f:
    cl = f.read()
check('changelog has 2026-08-23 W34 entry', '2026-08-23' in cl and 'W34' in cl)
import os
check('weekly report 2026-W34.md exists', os.path.isfile('/root/27-study/总结/每周/2026-W34.md'))

# ---- 6. task-reminder-data.py 数据源根治 ----
with open('/root/.hermes/profiles/408-study/scripts/task-reminder-data.py', encoding='utf-8') as f:
    trd = f.read()
check('task-reminder-data.py uses system date (no today_session.date dep)',
      'datetime.now().strftime("%Y-%m-%d")' in trd and 'state.get("today_session"' not in trd)
with open('/root/.hermes/scripts/task-reminder-data.py', encoding='utf-8') as f:
    trd2 = f.read()
check('global task-reminder-data.py copy also fixed', 'datetime.now().strftime("%Y-%m-%d")' in trd2)

# ---- 7. scripts syntactically valid ----
import ast
for s in ['/root/27-study/scripts/review-collect.py',
          '/root/27-study/scripts/review-dashboard-refresh.py',
          '/root/27-study/scripts/review-tasks.py',
          '/root/.hermes/profiles/408-study/scripts/task-reminder-data.py',
          '/root/.hermes/profiles/408-study/scripts/dashboard-refresh.py']:
    try:
        with open(s, encoding='utf-8') as f:
            ast.parse(f.read())
        check(f'{os.path.basename(s)} parses', True)
    except SyntaxError as e:
        check(f'{os.path.basename(s)} parses', False, str(e))

print('\n' + ('ALL CHECKS PASSED' if not fails else f'{len(fails)} CHECK(S) FAILED: {fails}'))
sys.exit(0 if not fails else 1)
