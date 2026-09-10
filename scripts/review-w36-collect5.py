# -*- coding: utf-8 -*-
"""W36 collector #5: 9/3 user interaction context + reminder content check."""
import sqlite3

DB = '/root/.hermes/profiles/408-study/state.db'
con = sqlite3.connect(DB)
cur = con.cursor()

print('=== weixin session msgs 2026-09-03 10:29 .. 10:40 ===')
cur.execute("""SELECT role, datetime(timestamp,'unixepoch','localtime') AS ts, substr(COALESCE(content,''),1,400)
               FROM messages WHERE session_id='20260803_175927_ed94bb12'
               AND timestamp BETWEEN strftime('%s','2026-09-03 10:29:00','utc') AND strftime('%s','2026-09-03 10:40:00','utc')
               ORDER BY timestamp""")
for r in cur.fetchall():
    print('---', r[0], r[1])
    print(r[2])

print('\n=== weixin session msgs 2026-09-01 .. 2026-09-06 (any) ===')
cur.execute("""SELECT role, datetime(timestamp,'unixepoch','localtime') AS ts, substr(COALESCE(content,''),1,120)
               FROM messages WHERE session_id='20260803_175927_ed94bb12'
               AND timestamp >= strftime('%s','2026-09-01 00:00:00','utc')
               ORDER BY timestamp""")
for r in cur.fetchall():
    print('---', r[0], r[1], '|', r[2])

print('\n=== weixin session: msgs since 8/11 (non-cron) around user msgs ===')
cur.execute("""SELECT COUNT(*) FROM messages WHERE session_id='20260803_175927_ed94bb12' AND timestamp >= strftime('%s','2026-08-11 00:00:00','utc')""")
print('total msgs in weixin session since 8/11:', cur.fetchone()[0])

print('\n=== assistant msgs in weixin session: last 8 by ts ===')
cur.execute("""SELECT datetime(timestamp,'unixepoch','localtime'), substr(COALESCE(content,''),1,150)
               FROM messages WHERE session_id='20260803_175927_ed94bb12' AND role='assistant'
               ORDER BY timestamp DESC LIMIT 8""")
for r in cur.fetchall():
    print('---', r[0], '|', r[1])
con.close()

print('\n=== cron output: 每日开课提醒 9/2 & 9/5 & 9/6 (first 600 chars each) ===')
import glob, os
for pat in ['2026-09-02_09-00-08.md', '2026-09-05_09-00-00.md', '2026-09-06_09-00-44.md']:
    fp = '/root/.hermes/profiles/408-study/cron/output/0d34337730f8/' + pat
    if os.path.exists(fp):
        s = open(fp, encoding='utf-8').read()
        print('=====', pat, 'len', len(s))
        print(s[:600])
    else:
        print('=====', pat, 'NOT FOUND')
