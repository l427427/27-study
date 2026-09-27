#!/usr/bin/env python3
# W39 周复盘数据采集（2026-09-27）
import json, os, sys, datetime, sqlite3

BASE = '/root/27-study'
SD = os.path.join(BASE, '状态数据')

def load(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)

rm = load(os.path.join(SD, 'roadmap.json'))
ss = load(os.path.join(SD, 'system-state.json'))
mas = load(os.path.join(SD, 'mastery.json'))

print("=== ROADMAP ===")
print("version:", rm.get('roadmap_version'), "| phases:", len(rm.get('phases', [])))
print("top keys:", list(rm.keys()))
tasks = rm.get('tasks', [])
print("total tasks:", len(tasks))
print("metadata:", json.dumps(rm.get('metadata'), ensure_ascii=False)[:600])

# phase status
for ph in rm.get('phases', []):
    print("  phase", ph.get('id'), ph.get('title'), ph.get('status'), ph.get('date_range') or (ph.get('start_date'), ph.get('end_date')))

# week window 9/21 - 9/27
print("\n=== 本周窗口任务 2026-09-21..2026-09-27 ===")
wk = [t for t in tasks if '2026-09-21' <= str(t.get('date','')) <= '2026-09-27']
print("count:", len(wk))
for t in wk:
    print(" ", t.get('id'), t.get('date'), t.get('status'), '|', str(t.get('title'))[:60], '| min=', t.get('minutes'), '| arch=', t.get('archived'), '| actual=', t.get('actual_date'))

print("\n=== 任务状态分布（全量） ===")
from collections import Counter
print(Counter(t.get('status') for t in tasks))
print("archived:", sum(1 for t in tasks if t.get('archived')))
print("date range:", min(str(t.get('date')) for t in tasks), "->", max(str(t.get('date')) for t in tasks))

print("\n=== 逾期（date < 9/27 且未完成且未归档） ===")
ov = [t for t in tasks if str(t.get('date','')) < '2026-09-27' and t.get('status') != 'completed' and not t.get('archived')]
print("count:", len(ov))
if ov:
    print("earliest:", min(str(t['date']) for t in ov), "| latest:", max(str(t['date']) for t in ov))
    c = Counter(str(t['date']) for t in ov)
    for d in sorted(c):
        print("   ", d, c[d])

print("\n=== 科目独立重数 ===")
subj = Counter()
for t in tasks:
    s = t.get('subject')
    subj[s if s else t.get('category')] += 1
for k, v in subj.items():
    print("  ", k, v)

print("\n=== MASTERY ===")
print(json.dumps(mas, ensure_ascii=False)[:500])

print("\n=== SYSTEM STATE ===")
print(json.dumps(ss, ensure_ascii=False, indent=1))
