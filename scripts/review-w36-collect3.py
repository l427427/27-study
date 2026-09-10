# -*- coding: utf-8 -*-
"""W36 collector #3: state.db sessions/messages/delivery evidence."""
import sqlite3, datetime

DB = '/root/.hermes/profiles/408-study/state.db'
con = sqlite3.connect(DB)
cur = con.cursor()

def dump_schema(t):
    cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (t,))
    r = cur.fetchone()
    print('--- schema', t, '---')
    print(r[0] if r else 'n/a')

for t in ['sessions', 'messages', 'delivery_obligations']:
    dump_schema(t)

print('\n=== sessions: source counts ===')
try:
    cur.execute("SELECT source, COUNT(*) FROM sessions GROUP BY source")
    for r in cur.fetchall():
        print(r)
except Exception as e:
    print('ERR', repr(e))

print('\n=== sessions: last 15 ===')
try:
    cur.execute("SELECT id, title, source, datetime(started_at,'unixepoch','localtime') FROM sessions ORDER BY rowid DESC LIMIT 15")
    cols = [d[0] for d in cur.description]
    print('cols:', cols)
    for r in cur.fetchall():
        print(r)
except Exception as e:
    print('ERR', repr(e))

print('\n=== delivery_obligations: last 20 ===')
try:
    cur.execute("SELECT * FROM delivery_obligations ORDER BY rowid DESC LIMIT 20")
    cols = [d[0] for d in cur.description]
    print('cols:', cols)
    for r in cur.fetchall():
        print(r)
except Exception as e:
    print('ERR', repr(e))

print('\n=== messages: role counts (total) ===')
try:
    cur.execute("SELECT role, COUNT(*) FROM messages GROUP BY role")
    for r in cur.fetchall():
        print(r)
except Exception as e:
    print('ERR', repr(e))

print('\n=== messages: last user msgs any time ===')
try:
    cur.execute("SELECT id, session_id, role, datetime(created_at,'unixepoch','localtime') AS ts, substr(content,1,80) FROM messages WHERE role='user' ORDER BY created_at DESC LIMIT 15")
    cols = [d[0] for d in cur.description]
    print('cols:', cols)
    for r in cur.fetchall():
        print(r)
except Exception as e:
    print('ERR', repr(e))
con.close()
