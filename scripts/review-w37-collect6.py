# -*- coding: utf-8 -*-
"""W37 collector #6: executions 表精确统计（schema + 本周按 job/日）。只读。"""
import sqlite3
from collections import Counter

p = '/root/.hermes/profiles/408-study/cron/executions.db'
con = sqlite3.connect('file:%s?mode=ro' % p, uri=True)
cur = con.cursor()
cur.execute("SELECT sql FROM sqlite_master WHERE name='executions'")
print('schema:', cur.fetchone()[0])
cur.execute("SELECT * FROM executions ORDER BY rowid DESC LIMIT 3")
cols = [d[0] for d in cur.description]
print('cols:', cols)
for r in cur.fetchall():
    print('  ', r)

print('\n=== 各 job 总执行数 ===')
cur.execute("SELECT job_id, COUNT(*) FROM executions GROUP BY job_id")
for r in cur.fetchall():
    print('  ', r)

print('\n=== 暂停的两个 job：最近 10 条执行（含时间列）===')
for c in cols:
    pass
cur.execute("SELECT rowid, job_id, datetime(COALESCE(process_started_at,0),'unixepoch','localtime'), * FROM executions WHERE job_id IN ('1e4a4ce7438c','5f3a2b1c9d8e') ORDER BY rowid DESC LIMIT 10")
for r in cur.fetchall():
    print('  ', str(r)[:260])
con.close()
