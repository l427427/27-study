#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ad-hoc verification for 2026-W36 weekly-review data changes (2026-09-06).
Checks: JSON validity, roadmap integrity (unchanged from W35: 205 tasks,
408 conservative contiguity 6→98), dashboard consistency vs roadmap
(W36 口径: overdue excl. archived = 106), system-state freshness (9/6, day 38),
changelog entry, high-frequency WeChat cron jobs paused (止血).
"""
import json, re, sys, os, ast

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

# ---- 2. roadmap integrity (unchanged content this week) ----
rm = load(BASE + 'roadmap.json')
tasks = rm['tasks']
check('roadmap has 205 tasks', len(tasks) == 205, str(len(tasks)))
ids = [t['id'] for t in tasks]
check('task ids unique', len(set(ids)) == len(ids))
req_keys = {'id', 'title', 'date', 'subject', 'phase_id', 'status', 'estimated_minutes'}
missing = [t['id'] for t in tasks if not req_keys.issubset(t.keys())]
check('all tasks have required keys', not missing, str(missing[:5]))

phases = {p['id']: p for p in rm['phases']}
check('phase-1 closed', phases['phase-1']['status'] == 'closed', phases['phase-1']['status'])
check('phase-2 closed', phases['phase-2']['status'] == 'closed', phases['phase-2']['status'])
check('phase-3 active', phases['phase-3']['status'] == 'active', phases['phase-3']['status'])
check('metadata.last_review updated to W36 (9/6)', '2026-09-06' in rm['metadata'].get('last_review', ''),
      rm['metadata'].get('last_review', '')[:50])

def lec_range(title):
    m = re.search(r'第(\d+)-(\d+)讲', title)
    return (int(m.group(1)), int(m.group(2))) if m else None

# phase-3 408 conservative contiguity 6→98
p3_408 = [t for t in tasks if t.get('phase_id') == 'phase-3' and t.get('subject') == '408']
check('phase-3 has 31 408 tasks', len(p3_408) == 31, str(len(p3_408)))
p3_408 = sorted(p3_408, key=lambda x: x['date'])
r3 = [lec_range(t['title']) for t in p3_408]
contig3 = all(r3[i][0] == (5 if i == 0 else r3[i-1][1]) + 1 for i in range(len(r3)))
check('phase-3 408 contiguous from 6 (conservative)', contig3, f'{r3[0]}..{r3[-1]}')
check('phase-3 408 ends at 96-98', r3[-1] == (96, 98), str(r3[-1]))
p3_per_day = {}
for t in tasks:
    if t.get('phase_id') == 'phase-3':
        p3_per_day[t['date']] = p3_per_day.get(t['date'], 0) + 1
check('phase-3 = 3 tasks/day x 31 days', set(p3_per_day.values()) == {3} and len(p3_per_day) == 31)

# ---- 3. dashboard consistency vs roadmap ----
db = load(BASE + 'dashboard-data.json')
exp_keys = {'dashboard_version','generated_at','summary','progress','tasks','subjects','phases','recent_activities','status'}
check('dashboard schema keys intact', exp_keys.issubset(db.keys()))
check('dashboard total=205', db['tasks']['total_tasks'] == 205, str(db['tasks']['total_tasks']))
check('dashboard completed=0 (no fabrication)', db['tasks']['completed_tasks'] == 0)
check('dashboard pending=205', db['tasks']['pending_tasks'] == 205)
overdue_manual = sum(1 for t in tasks if (t.get('date') or '') < '2026-09-06'
                     and t.get('status') != 'completed' and not t.get('archived'))
check('dashboard overdue=106 (excl. archived, recount)', db['tasks']['overdue_tasks'] == overdue_manual == 106,
      f"dashboard={db['tasks']['overdue_tasks']}, recount={overdue_manual}")
check('dashboard current_day=38', db['progress']['current_day'] == 38, str(db['progress']['current_day']))
check('dashboard days_remaining=110', db['progress']['days_remaining'] == 110, str(db['progress']['days_remaining']))
subj = {}
for t in tasks:
    subj[t['subject']] = subj.get(t['subject'], 0) + 1
dsubj = {k: v['total_tasks'] for k, v in db['subjects'].items() if v['total_tasks'] > 0}
check('dashboard subject counts == roadmap counts', subj == dsubj, f'{subj} vs {dsubj}')
check('subject counts sum to 205', sum(dsubj.values()) == 205, str(sum(dsubj.values())))

# ---- 4. system-state freshness ----
ss = load(BASE + 'system-state.json')
check('system-state current_day=38', ss['current_project']['current_day'] == 38, str(ss['current_project']['current_day']))
check('system-state today=9/6', ss['today_session']['date'] == '2026-09-06', ss['today_session']['date'])
check('system-state last_session 8/6 no_report (unchanged)',
      ss['last_session']['date'] == '2026-08-06' and ss['last_session']['status'] == 'no_report')

# ---- 5. changelog + weekly report ----
with open(BASE + 'roadmap-changelog.md', encoding='utf-8') as f:
    cl = f.read()
check('changelog has 2026-09-06 W36 entry', '2026-09-06' in cl and 'W36' in cl and '止血' in cl)
check('weekly report 2026-W36.md exists', os.path.isfile('/root/27-study/总结/每周/2026-W36.md'))
w36 = open('/root/27-study/总结/每周/2026-W36.md', encoding='utf-8').read()
check('W36 report mentions 9/3 user contact', '9/3' in w36 and '从头开始任务' in w36)

# ---- 6. high-frequency WeChat jobs paused (止血) ----
jobs = json.load(open('/root/.hermes/profiles/408-study/cron/jobs.json', encoding='utf-8'))
jm = {j['id']: j for j in jobs['jobs']}
check('1e4a4ce7438c (逐项提醒) paused', jm['1e4a4ce7438c'].get('enabled') is False
      or jm['1e4a4ce7438c'].get('state') == 'paused', str(jm['1e4a4ce7438c'].get('state')))
check('5f3a2b1c9d8e (轮换提醒) paused', jm['5f3a2b1c9d8e'].get('enabled') is False
      or jm['5f3a2b1c9d8e'].get('state') == 'paused', str(jm['5f3a2b1c9d8e'].get('state')))
check('0d34337730f8 (早 9:00) still enabled', jm['0d34337730f8'].get('enabled') is not False,
      str(jm['0d34337730f8'].get('state')))
check('55bd60a924fd (晚 21:00) still enabled', jm['55bd60a924fd'].get('enabled') is not False,
      str(jm['55bd60a924fd'].get('state')))

# ---- 7. reminder scripts still on system-date source ----
with open('/root/.hermes/profiles/408-study/scripts/task-reminder-data.py', encoding='utf-8') as f:
    trd = f.read()
check('task-reminder-data.py uses system date', 'datetime.now()' in trd and 'strftime("%Y-%m-%d")' in trd)
with open('/root/.hermes/profiles/408-study/scripts/daily-opening-data.py', encoding='utf-8') as f:
    dod = f.read()
check('daily-opening-data.py uses system date', 'datetime.now()' in dod and 'strftime("%Y-%m-%d")' in dod)

# ---- 8. scripts syntactically valid ----
for s in ['/root/27-study/scripts/review-w36-collect.py',
          '/root/27-study/scripts/review-w36-collect2.py',
          '/root/27-study/scripts/review-w36-calibrate.py',
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
