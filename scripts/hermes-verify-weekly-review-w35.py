#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ad-hoc verification for 2026-W35 weekly-review data changes (2026-08-30).
Checks: JSON validity, roadmap phase transition + phase-3 generation (t113-t205,
408 conservative re-plan contiguity 6→98), dashboard consistency vs roadmap
(W35 口径: total=205, overdue excl. archived=88), system-state freshness (8/30, day30).
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

# ---- 2. roadmap integrity ----
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
check('phase-2 closed (8/27 结营)', phases['phase-2']['status'] == 'closed', phases['phase-2']['status'])
check('phase-3 active', phases['phase-3']['status'] == 'active', phases['phase-3']['status'])
check('phase-3 goal conservative re-plan', '保守基线' in phases['phase-3']['goal'], phases['phase-3']['goal'][:40])

def lec_range(title):
    m = re.search(r'第(\d+)-(\d+)讲', title)
    return (int(m.group(1)), int(m.group(2))) if m else None

# phase-1/2 408: calibration set (t039..t111) contiguity 6→52 (unchanged history)
# 注意排除 archived（t003/t009/t015/t021 为重置前旧任务）与校准前遗留（t027/t033）
calib_ids = {'t039','t045','t051','t056','t059','t062','t065','t068','t071','t074',
             't077','t080','t083','t086','t089','t092','t095','t098','t101','t104','t107','t111'}
old408 = [t for t in tasks if t['id'] in calib_ids and t.get('subject') == '408'
          and lec_range(t['title']) and not t.get('archived')]
check('phase-1/2 calibration set complete (22 tasks)', len(old408) == 22, str(len(old408)))
ranges = [lec_range(t['title']) for t in sorted(old408, key=lambda x: int(x['id'][1:]))]
contig = all(ranges[i][0] == (5 if i == 0 else ranges[i-1][1]) + 1 for i in range(len(ranges)))
check('phase-1/2 408 contiguous from 6', contig, f'{ranges[0]}..{ranges[-1]}')
check('phase-1/2 408 ends at 51-52', ranges[-1] == (51, 52), str(ranges[-1]))

# phase-3 408: conservative re-plan contiguity 6→98
p3_408 = [t for t in tasks if t.get('phase_id') == 'phase-3' and t.get('subject') == '408']
check('phase-3 has 31 408 tasks (8/31-9/30)', len(p3_408) == 31, str(len(p3_408)))
p3_408 = sorted(p3_408, key=lambda x: x['date'])
r3 = [lec_range(t['title']) for t in p3_408]
contig3 = all(r3[i][0] == (5 if i == 0 else r3[i-1][1]) + 1 for i in range(len(r3)))
check('phase-3 408 contiguous from 6 (conservative)', contig3, f'{r3[0]}..{r3[-1]}')
check('phase-3 408 ends at 96-98 (9/30)', r3[-1] == (96, 98), str(r3[-1]))
p3_dates = sorted(set(t['date'] for t in tasks if t.get('phase_id') == 'phase-3'))
check('phase-3 tasks span 8/31-9/30 only', p3_dates[0] == '2026-08-31' and p3_dates[-1] == '2026-09-30',
      f'{p3_dates[0]}..{p3_dates[-1]}')
p3_per_day = {}
for t in tasks:
    if t.get('phase_id') == 'phase-3':
        p3_per_day[t['date']] = p3_per_day.get(t['date'], 0) + 1
check('phase-3 = 3 tasks per day x 31 days', set(p3_per_day.values()) == {3} and len(p3_per_day) == 31,
      str(len(p3_per_day)))
stale = [t['id'] for t in tasks if t.get('subject') == '408' and t.get('phase_id') == 'phase-3'
         and lec_range(t['title']) and lec_range(t['title'])[1] > 98]
check('no phase-3 408 beyond lecture 98', not stale, str(stale))

check('metadata.last_review updated to W35',
      '2026-08-30' in (rm['metadata'].get('last_review') or '') and 'W35' in (rm['metadata'].get('last_review') or ''),
      str(rm['metadata'].get('last_review')))

# ---- 3. dashboard consistency vs roadmap ----
db = load(BASE + 'dashboard-data.json')
exp_keys = {'dashboard_version','generated_at','summary','progress','tasks','subjects','phases','recent_activities','status'}
check('dashboard schema keys intact', exp_keys.issubset(db.keys()))
check('dashboard total=205', db['tasks']['total_tasks'] == 205, str(db['tasks']['total_tasks']))
check('dashboard completed=0 (no fabrication)', db['tasks']['completed_tasks'] == 0)
check('dashboard pending=205', db['tasks']['pending_tasks'] == 205)
overdue_manual = sum(1 for t in tasks if (t.get('date') or '') < '2026-08-30'
                     and t.get('status') != 'completed' and not t.get('archived'))
check('dashboard overdue=88 (excl. archived, recount)', db['tasks']['overdue_tasks'] == overdue_manual == 88,
      f"dashboard={db['tasks']['overdue_tasks']}, recount={overdue_manual}")
check('dashboard current_day=30', db['progress']['current_day'] == 30, str(db['progress']['current_day']))
check('dashboard days_remaining=118', db['progress']['days_remaining'] == 118, str(db['progress']['days_remaining']))
check('dashboard phase-1/2 closed, phase-3 active',
      db['phases']['phase-1']['status'] == 'closed' and db['phases']['phase-2']['status'] == 'closed'
      and db['phases']['phase-3']['status'] == 'active')

subj = {}
for t in tasks:
    subj[t['subject']] = subj.get(t['subject'], 0) + 1
dsubj = {k: v['total_tasks'] for k, v in db['subjects'].items() if v['total_tasks'] > 0}
check('dashboard subject counts == roadmap counts (zero-total extras allowed)',
      subj == dsubj, f'{subj} vs {dsubj}')
check('subject counts sum to 205', sum(dsubj.values()) == 205, str(sum(dsubj.values())))

# ---- 4. system-state freshness ----
ss = load(BASE + 'system-state.json')
check('system-state current_day=30', ss['current_project']['current_day'] == 30, str(ss['current_project']['current_day']))
check('system-state today=8/30', ss['today_session']['date'] == '2026-08-30', ss['today_session']['date'])
check('system-state last_session 8/6 no_report',
      ss['last_session']['date'] == '2026-08-06' and ss['last_session']['status'] == 'no_report')

# ---- 5. changelog + weekly report ----
with open(BASE + 'roadmap-changelog.md', encoding='utf-8') as f:
    cl = f.read()
check('changelog has 2026-08-30 W35 entry', '2026-08-30' in cl and 'W35' in cl)
check('weekly report 2026-W35.md exists', os.path.isfile('/root/27-study/总结/每周/2026-W35.md'))

# ---- 6. reminder scripts still on system-date source ----
with open('/root/.hermes/profiles/408-study/scripts/task-reminder-data.py', encoding='utf-8') as f:
    trd = f.read()
check('task-reminder-data.py uses system date', 'datetime.now().strftime("%Y-%m-%d")' in trd
      and 'state.get("today_session"' not in trd)
with open('/root/.hermes/profiles/408-study/scripts/daily-opening-data.py', encoding='utf-8') as f:
    dod = f.read()
check('daily-opening-data.py uses system date', 'datetime.now()' in dod and 'strftime("%Y-%m-%d")' in dod)

# ---- 7. scripts syntactically valid ----
for s in ['/root/27-study/scripts/review-w35-calibrate.py',
          '/root/27-study/scripts/review-w35-dashboard-refresh.py',
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
