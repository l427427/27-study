#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ad-hoc verification for 2026-W37 weekly-review data changes (2026-09-13).

镜像 hermes-verify-weekly-review-w36.py，按 W37 期望值更新断言：
 JSON 合法性 / roadmap 完整性（内容不变：205 项、408 保守连续 6→98）/
 dashboard 与 roadmap 独立重数一致（overdue 排除 archived = 127）/
 system-state 新鲜度（9/13、day 44）/ changelog 追加 / W37 周报落盘 /
 高频微信 job 仍暂停（止血）/ .env 熔断已放宽（120s, threshold 2）/
 提醒脚本仍用系统日期 / 脚本语法可解析。
"""
import ast
import json
import os
import re
import sys

BASE = '/root/27-study/状态数据/'
fails = []


def check(name, cond, detail=''):
    print('[%s] %s%s' % ('PASS' if cond else 'FAIL', name, ' — ' + detail if detail else ''))
    if not cond:
        fails.append(name)


def load(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)


# ---- 1. JSON validity ----
for fn in ['system-state.json', 'roadmap.json', 'dashboard-data.json', 'mastery.json', 'exam-schedule.json']:
    try:
        load(BASE + fn)
        check('%s valid JSON' % fn, True)
    except Exception as e:
        check('%s valid JSON' % fn, False, str(e))

# ---- 2. roadmap integrity (内容本周不变) ----
rm = load(BASE + 'roadmap.json')
tasks = rm['tasks']
check('roadmap has 205 tasks', len(tasks) == 205, str(len(tasks)))
ids = [t['id'] for t in tasks]
check('task ids unique', len(set(ids)) == len(ids))
req = {'id', 'title', 'date', 'subject', 'phase_id', 'status', 'estimated_minutes'}
missing = [t['id'] for t in tasks if not req.issubset(t.keys())]
check('all tasks have required keys', not missing, str(missing[:5]))
check('no task marked completed (no fabrication)',
      sum(1 for t in tasks if t.get('status') == 'completed') == 0)

phases = {p['id']: p for p in rm['phases']}
check('phase-1 closed', phases['phase-1']['status'] == 'closed', phases['phase-1']['status'])
check('phase-2 closed', phases['phase-2']['status'] == 'closed', phases['phase-2']['status'])
check('phase-3 active', phases['phase-3']['status'] == 'active', phases['phase-3']['status'])
check('metadata.last_review updated to W37 (9/13)', '2026-09-13' in rm['metadata'].get('last_review', ''),
      rm['metadata'].get('last_review', '')[:60])
check('metadata.last_review keeps W37 fault finding',
      'prepare failed' in rm['metadata'].get('last_review', '')
      and 'H15' in rm['metadata'].get('last_review', ''))


def lec_range(title):
    m = re.search(r'第(\d+)-(\d+)讲', title)
    return (int(m.group(1)), int(m.group(2))) if m else None


p3_408 = [t for t in tasks if t.get('phase_id') == 'phase-3' and t.get('subject') == '408']
check('phase-3 has 31 408 tasks', len(p3_408) == 31, str(len(p3_408)))
p3_408 = sorted(p3_408, key=lambda x: x['date'])
r3 = [lec_range(t['title']) for t in p3_408]
contig3 = all(r3[i][0] == (5 if i == 0 else r3[i - 1][1]) + 1 for i in range(len(r3)))
check('phase-3 408 contiguous from 6 (conservative)', contig3, '%s..%s' % (r3[0], r3[-1]))
check('phase-3 408 ends at 96-98', r3[-1] == (96, 98), str(r3[-1]))
per_day = {}
for t in tasks:
    if t.get('phase_id') == 'phase-3':
        per_day[t['date']] = per_day.get(t['date'], 0) + 1
check('phase-3 = 3 tasks/day x 31 days', set(per_day.values()) == {3} and len(per_day) == 31)

# W37 窗口 21 项 t134-t154
w37 = [t for t in tasks if '2026-09-07' <= (t.get('date') or '') <= '2026-09-13' and not t.get('archived')]
check('W37 window has 21 tasks (t134-t154)', len(w37) == 21 and min(t['id'] for t in w37) == 't134'
      and max(t['id'] for t in w37) == 't154', '%d %s..%s' % (len(w37), min(t['id'] for t in w37), max(t['id'] for t in w37)))

# ---- 3. dashboard consistency vs roadmap ----
db = load(BASE + 'dashboard-data.json')
exp_keys = {'dashboard_version', 'generated_at', 'summary', 'progress', 'tasks', 'subjects', 'phases',
            'recent_activities', 'status'}
check('dashboard schema keys intact', exp_keys.issubset(db.keys()))
check('dashboard total=205', db['tasks']['total_tasks'] == 205, str(db['tasks']['total_tasks']))
check('dashboard completed=0 (no fabrication)', db['tasks']['completed_tasks'] == 0)
check('dashboard pending=205', db['tasks']['pending_tasks'] == 205)
overdue_manual = sum(1 for t in tasks if (t.get('date') or '') < '2026-09-13'
                     and t.get('status') != 'completed' and not t.get('archived'))
check('dashboard overdue=127 (excl. archived, recount)',
      db['tasks']['overdue_tasks'] == overdue_manual == 127,
      'dashboard=%s, recount=%s' % (db['tasks']['overdue_tasks'], overdue_manual))
check('dashboard current_day=44', db['progress']['current_day'] == 44, str(db['progress']['current_day']))
check('dashboard days_remaining=104', db['progress']['days_remaining'] == 104, str(db['progress']['days_remaining']))
subj = {}
for t in tasks:
    subj[t['subject']] = subj.get(t['subject'], 0) + 1
dsubj = {k: v['total_tasks'] for k, v in db['subjects'].items() if v['total_tasks'] > 0}
check('dashboard subject counts == roadmap counts', subj == dsubj, '%s vs %s' % (subj, dsubj))
check('subject counts sum to 205', sum(dsubj.values()) == 205, str(sum(dsubj.values())))

# ---- 4. system-state freshness ----
ss = load(BASE + 'system-state.json')
check('system-state current_day=44', ss['current_project']['current_day'] == 44,
      str(ss['current_project']['current_day']))
check('system-state today=2026-09-13', ss['today_session']['date'] == '2026-09-13', ss['today_session']['date'])
check('system-state today_session day_closed', ss['today_session']['status'] == 'day_closed')
check('system-state last_session=9/3 no_report (user inbound unanswered)',
      ss['last_session']['date'] == '2026-09-03' and ss['last_session']['status'] == 'no_report',
      json.dumps(ss['last_session'], ensure_ascii=False)[:80])

# ---- 5. changelog + weekly report ----
with open(BASE + 'roadmap-changelog.md', encoding='utf-8') as f:
    cl = f.read()
check('changelog has 2026-09-13 W37 entry', '2026-09-13' in cl and 'W37' in cl)
check('changelog records the local circuit-breaker finding', '熔断' in cl and 'prepare failed' in cl)
check('changelog records H10 refutation', 'H10' in cl)
check('weekly report 2026-W37.md exists', os.path.isfile('/root/27-study/总结/每周/2026-W37.md'))
w37md = open('/root/27-study/总结/每周/2026-W37.md', encoding='utf-8').read()
check('W37 report mentions 9/3 user contact', '9/3' in w37md and '从头开始任务' in w37md)
check('W37 report covers all 7 review sections',
      all(k in w37md for k in ['本周计划 vs 实际完成', '投入时间、节奏与掌握度', '真正学会 vs 仍不稳定',
                               '高频错题', 'Roadmap 本周调整', '学习模式识别', '下周建议']))
check('W37 report states failure signature', 'prepare failed' in w37md)
check('W37 report keeps 408 baseline = 第 5 讲', '第 5 讲' in w37md)
check('W37 report does not fabricate study records', '不补写缺勤日' in w37md)

# ---- 6. WeChat high-frequency jobs still paused (止血) ----
jobs = json.load(open('/root/.hermes/profiles/408-study/cron/jobs.json', encoding='utf-8'))
jm = {j['id']: j for j in jobs['jobs']}
for jid, name in [('1e4a4ce7438c', '逐项提醒'), ('5f3a2b1c9d8e', '轮换提醒')]:
    check('%s (%s) paused' % (jid, name),
          jm[jid].get('enabled') is False or jm[jid].get('state') == 'paused', str(jm[jid].get('state')))
for jid, name in [('0d34337730f8', '早 9:00'), ('55bd60a924fd', '晚 21:00')]:
    check('%s (%s) still enabled' % (jid, name), jm[jid].get('enabled') is not False, str(jm[jid].get('state')))

# ---- 7. .env 熔断放宽（本周新动作） ----
envp = '/root/.hermes/profiles/408-study/.env'
env = {}
for line in open(envp, encoding='utf-8'):
    line = line.strip()
    if line and not line.startswith('#') and '=' in line:
        k, v = line.split('=', 1)
        env[k.strip()] = v.strip()
check('.env circuit open lowered to 120', env.get('WEIXIN_RATE_LIMIT_CIRCUIT_OPEN_SECONDS') == '120',
      str(env.get('WEIXIN_RATE_LIMIT_CIRCUIT_OPEN_SECONDS')))
check('.env circuit threshold set to 2', env.get('WEIXIN_RATE_LIMIT_CIRCUIT_THRESHOLD') == '2',
      str(env.get('WEIXIN_RATE_LIMIT_CIRCUIT_THRESHOLD')))
check('.env backup created (.bak-w37)', os.path.isfile(envp + '.bak-w37'))
check('.env backup keeps old 600 value',
      'WEIXIN_RATE_LIMIT_CIRCUIT_OPEN_SECONDS=600' in open(envp + '.bak-w37', encoding='utf-8').read())
check('.env still has WEIXIN_TOKEN/ACCOUNT_ID', 'WEIXIN_TOKEN' in env and 'WEIXIN_ACCOUNT_ID' in env)

# ---- 8. reminder scripts still on system-date source ----
for s in ['/root/.hermes/profiles/408-study/scripts/task-reminder-data.py',
          '/root/.hermes/profiles/408-study/scripts/daily-opening-data.py']:
    src = open(s, encoding='utf-8').read()
    check('%s uses system date' % os.path.basename(s),
          'datetime.now()' in src and 'strftime("%Y-%m-%d")' in src)

# ---- 9. scripts syntactically valid ----
for s in ['/root/27-study/scripts/review-w37-collect.py',
          '/root/27-study/scripts/review-w37-collect2.py',
          '/root/27-study/scripts/review-w37-collect3.py',
          '/root/27-study/scripts/review-w37-collect4.py',
          '/root/27-study/scripts/review-w37-collect5.py',
          '/root/27-study/scripts/review-w37-collect6.py',
          '/root/27-study/scripts/review-w37-collect7.py',
          '/root/27-study/scripts/review-w37-calibrate2.py',
          '/root/27-study/scripts/review-w37-dashboard.py',
          '/root/.hermes/profiles/408-study/scripts/dashboard-refresh.py']:
    try:
        ast.parse(open(s, encoding='utf-8').read())
        check('%s parses' % os.path.basename(s), True)
    except SyntaxError as e:
        check('%s parses' % os.path.basename(s), False, str(e))

print('\n' + ('ALL CHECKS PASSED' if not fails else '%d CHECK(S) FAILED: %s' % (len(fails), fails)))
sys.exit(0 if not fails else 1)
