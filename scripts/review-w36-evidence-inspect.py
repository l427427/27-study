# -*- coding: utf-8 -*-
"""Inspect verification_evidence.db schema + recent rows."""
import sqlite3

con = sqlite3.connect('/root/.hermes/profiles/408-study/verification_evidence.db')
cur = con.cursor()
cur.execute("SELECT sql FROM sqlite_master WHERE type='table'")
for r in cur.fetchall():
    print(r[0])
print('--- tables ---')
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print([r[0] for r in cur.fetchall()])
for t in [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")]:
    try:
        cur.execute(f'SELECT COUNT(*) FROM {t}')
        print(t, 'rows:', cur.fetchone()[0])
    except Exception as e:
        print(t, 'ERR', e)
