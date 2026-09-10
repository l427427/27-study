# -*- coding: utf-8 -*-
"""W36 collector #6: cron executions delivery-failure quantification."""
import sqlite3

con = sqlite3.connect('/root/.hermes/profiles/408-study/cron/executions.db')
cur = con.cursor()
print('=== executions 8/31-9/6 by job & status ===')
cur.execute("SELECT job_id, status, COUNT(*) FROM executions WHERE started_at >= '2026-08-31' GROUP BY job_id, status")
for r in cur.fetchall():
    print(r)
print('=== rate-limited errors per day (8/28-9/6) ===')
cur.execute("SELECT substr(finished_at,1,10) d, COUNT(*) FROM executions WHERE error LIKE '%rate limited%' AND finished_at >= '2026-08-28' GROUP BY d ORDER BY d")
for r in cur.fetchall():
    print(r)
print('=== total executions per job 8/28-9/6 ===')
cur.execute("SELECT job_id, COUNT(*) FROM executions WHERE started_at >= '2026-08-28' GROUP BY job_id")
for r in cur.fetchall():
    print(r)
print('=== sample execution rows w/ error (last 6) ===')
cur.execute("SELECT job_id, substr(started_at,1,16), status, substr(COALESCE(error,''),1,90) FROM executions ORDER BY rowid DESC LIMIT 6")
for r in cur.fetchall():
    print(r)
con.close()
