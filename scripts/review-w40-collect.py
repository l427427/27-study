#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""W40 周复盘数据采集（2026-10-04，窗口 9/28–10/4）"""
import json, os, sqlite3
from collections import Counter

BASE = '/root/27-study'
SD = os.path.join(BASE, '状态数据')
DB = '/root/.hermes/profiles/408-study/state.db'

def load(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)

rm = load(os.path.join(SD, 'roadmap.json'))
ss = load(os.path.join(SD, 'system-state.json'))
mas = load(os.path.join(SD, 'mastery.json'))
tasks = rm.get('tasks', [])

print("=== ROADMAP ===")
print("version:", rm.get('roadmap_version'), "| total tasks:", len(tasks))
for ph in rm.get('phases', []):
    print("  ", ph.get('id'), ph.get('status'), ph.get('date_range'))

print("\n=== 本周窗口任务 2026-09-28..2026-10-04 ===")
wk = [t for t in tasks if '2026-09-28' <= str(t.get('date','')) <= '2026-10-04']
print("count:", len(wk))
for t in wk:
    print("  ", t.get('id'), t.get('date'), t.get('status'), '|', str(t.get('title'))[:55],
          '| min=', t.get('minutes'), '| arch=', t.get('archived'), '| actual=', t.get('actual_date'))

print("\n=== 全量状态分布 ===")
print(Counter(t.get('status') for t in tasks))
print("archived:", sum(1 for t in tasks if t.get('archived')))
print("date range:", min(str(t.get('date')) for t in tasks), "->", max(str(t.get('date')) for t in tasks))

print("\n=== 逾期（date < 2026-10-04 且未完成且未归档）===")
ov = [t for t in tasks if str(t.get('date','')) < '2026-10-04' and t.get('status') != 'completed' and not t.get('archived')]
print("count:", len(ov))
if ov:
    print("earliest:", min(str(t['date']) for t in ov), "| latest:", max(str(t['date'])) if False else max(str(t['date']) for t in ov))
    c = Counter(str(t['date']) for t in ov)
    print("  按日:", dict(sorted(c.items())[:5]), "...", dict(sorted(c.items())[-5:]))

print("\n=== 科目独立重数 ===")
subj = Counter()
for t in tasks:
    s = t.get('subject') or t.get('category') or '?'
    subj[s] += 1
for k, v in sorted(subj.items()):
    print("  ", k, v)
print("  sum:", sum(subj.values()))

print("\n=== 10/1-10/4 是否有排期 ===")
print("日期 >= 2026-10-01 的任务数:", sum(1 for t in tasks if str(t.get('date','')) >= '2026-10-01'))

print("\n=== MASTERY ===")
print(json.dumps(mas, ensure_ascii=False))
print("\n=== SYSTEM STATE ===")
print(json.dumps(ss, ensure_ascii=False, indent=1))

print("\n=== STATE.DB：真人入站 vs cron 自触发 ===")
con = sqlite3.connect(DB)
cur = con.cursor()
cur.execute("""
 SELECT datetime(m.timestamp,'unixepoch','+8 hours'), s.source, substr(replace(m.content,char(10),' '),1,70)
 FROM messages m JOIN sessions s ON m.session_id = s.id
 WHERE m.role='user' AND m.timestamp >= strftime('%s','2026-09-27 16:00:00')
   AND m.content NOT LIKE '[IMPORTANT:%'
 ORDER BY m.timestamp""")
rows = cur.fetchall()
print("本周非cron自触发的 user 消息数:", len(rows))
for r in rows:
    print("  ", r)

cur.execute("""
 SELECT datetime(m.timestamp,'unixepoch','+8 hours'), s.source, substr(replace(m.content,char(10),' '),1,70)
 FROM messages m JOIN sessions s ON m.session_id = s.id
 WHERE m.role='user' AND m.content NOT LIKE '[IMPORTANT:%'
 ORDER BY m.timestamp DESC LIMIT 6""")
print("最后真人入站:")
for r in cur.fetchall():
    print("  ", r)

cur.execute("SELECT count(*), min(datetime(timestamp,'unixepoch','+8 hours')), max(datetime(timestamp,'unixepoch','+8 hours')) FROM messages WHERE timestamp >= strftime('%s','2026-09-27 16:00:00') AND content LIKE '[IMPORTANT:%'")
print("本周 cron 自触发 prompt 行:", cur.fetchone())

cur.execute("PRAGMA table_info(delivery_obligations)")
cols = [c[1] for c in cur.fetchall()]
print("delivery_obligations cols:", cols)
cur.execute("SELECT count(*) FROM delivery_obligations")
print("obligations total:", cur.fetchone()[0])
cur.execute("SELECT id, platform, substr(coalesce(status,''),0,20), substr(coalesce(error,''),0,60) FROM delivery_obligations LIMIT 5") if 'status' in cols else None
try:
    cur.execute("SELECT id, coalesce(last_error,'') FROM delivery_obligations LIMIT 5")
    for r in cur.fetchall():
        print("  ob:", str(r)[:160])
except Exception as e:
    print("  (err)", e)
con.close()
