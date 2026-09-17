# -*- coding: utf-8 -*-
"""W37 collector #3: 9/10-9/13 cron sessions + jobs.json 状态。只读。"""
import sqlite3, json, os

DB = '/root/.hermes/profiles/408-study/state.db'
con = sqlite3.connect(DB)
cur = con.cursor()

print('=== cron sessions 9/09 起 ===')
cur.execute("SELECT id, substr(title,1,60), datetime(started_at,'unixepoch','localtime'), message_count FROM sessions WHERE started_at >= strftime('%s','2026-09-09 00:00:00','utc') ORDER BY started_at")
for r in cur.fetchall():
    print('  ', r)

print('\n=== 9/10 12:00-13:00 之间有无 session（校准脚本作者）===')
cur.execute("SELECT id, source, substr(title,1,60), datetime(started_at,'unixepoch','localtime') FROM sessions WHERE started_at BETWEEN strftime('%s','2026-09-10 11:00:00','utc') AND strftime('%s','2026-09-10 14:00:00','utc')")
for r in cur.fetchall():
    print('  ', r)

print('\n=== 9/07 起 user 消息（排除 cron 模板）===')
cur.execute("""SELECT datetime(timestamp,'unixepoch','localtime'), substr(content,1,120) FROM messages
               WHERE role='user' AND timestamp >= strftime('%s','2026-09-07 00:00:00','utc')
                 AND content NOT LIKE '[IMPORTANT: The user has invoked%'
               ORDER BY timestamp""")
rows = cur.fetchall()
print('  real-user count =', len(rows))
for r in rows:
    print('  ', r)

print('\n=== jobs.json 位置与内容摘要 ===')
cands = ['/root/.hermes/profiles/408-study/cron/jobs.json',
         '/root/.hermes/cron/jobs.json']
for p in cands:
    print(' exists', p, os.path.exists(p))
    if os.path.exists(p):
        try:
            j = json.load(open(p, encoding='utf-8'))
            jobs = j.get('jobs', j) if isinstance(j, dict) else j
            if isinstance(jobs, dict):
                jobs = list(jobs.values())
            print('  n jobs =', len(jobs))
            for it in jobs:
                if not isinstance(it, dict):
                    continue
                print('   - %s | %s | state=%s | sched=%s | deliver=%s' % (
                    it.get('id'), it.get('name'), it.get('state', it.get('enabled')),
                    it.get('schedule'), str(it.get('deliver'))[:40]))
        except Exception as e:
            print('  parse err', e)

print('\n=== jobs.json 投递错误（逐 job）===')
for p in cands:
    if not os.path.exists(p):
        continue
    j = json.load(open(p, encoding='utf-8'))
    jobs = j.get('jobs', j) if isinstance(j, dict) else j
    if isinstance(jobs, dict):
        jobs = list(jobs.values())
    for it in jobs:
        if isinstance(it, dict) and it.get('last_delivery_error'):
            print('  %s (%s): %s' % (it.get('name'), it.get('id'), str(it['last_delivery_error'])[:160]))
            print('     last_run=%s status=%s' % (it.get('last_run_at'), it.get('last_run_status')))
con.close()
