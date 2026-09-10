# -*- coding: utf-8 -*-
"""W36 collector #4: user inbound timeline + delivery outcomes."""
import sqlite3, datetime

DB = '/root/.hermes/profiles/408-study/state.db'
con = sqlite3.connect(DB)
cur = con.cursor()

print('=== weixin session ===')
cur.execute("SELECT id, source, title, datetime(started_at,'unixepoch','localtime'), datetime(last_activity_at,'unixepoch','localtime'), message_count, chat_id FROM sessions WHERE source='weixin'")
cols = [d[0] for d in cur.description]
print('cols:', cols)
for r in cur.fetchall():
    print(r)

print('\n=== user messages: last 25 by timestamp ===')
cur.execute("SELECT id, session_id, datetime(timestamp,'unixepoch','localtime') AS ts, substr(content,1,90) FROM messages WHERE role='user' ORDER BY timestamp DESC LIMIT 25")
for r in cur.fetchall():
    print(r)

print('\n=== user messages per day (all time, last 40 days) ===')
cur.execute("SELECT date(timestamp,'unixepoch','localtime') AS d, COUNT(*) FROM messages WHERE role='user' GROUP BY d ORDER BY d DESC LIMIT 40")
for r in cur.fetchall():
    print(r)

print('\n=== user message count since 2026-08-11 ===')
cur.execute("SELECT COUNT(*) FROM messages WHERE role='user' AND timestamp >= strftime('%s','2026-08-11 00:00:00','utc')")
print('count:', cur.fetchone()[0])

print('\n=== delivery_obligations by state ===')
cur.execute("SELECT state, COUNT(*) FROM delivery_obligations GROUP BY state")
for r in cur.fetchall():
    print(r)

print('\n=== delivery_obligations: updated per day 08-28..09-06 ===')
cur.execute("SELECT date(updated_at,'unixepoch','localtime') AS d, state, COUNT(*) FROM delivery_obligations WHERE updated_at >= strftime('%s','2026-08-28 00:00:00','utc') GROUP BY d, state ORDER BY d")
for r in cur.fetchall():
    print(r)

print('\n=== delivery_obligations: last 10 created ===')
cur.execute("SELECT obligation_id, substr(content,1,50), state, attempts, datetime(created_at,'unixepoch','localtime'), datetime(updated_at,'unixepoch','localtime'), substr(last_error,1,60) FROM delivery_obligations ORDER BY created_at DESC LIMIT 10")
for r in cur.fetchall():
    print(r)

print('\n=== executions.db: schema ===')
cur2 = sqlite3.connect('/root/.hermes/profiles/408-study/cron/executions.db').cursor()
cur2.execute("SELECT sql FROM sqlite_master WHERE type='table'")
print(cur2.fetchone()[0])
