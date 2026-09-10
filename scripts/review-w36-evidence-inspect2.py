# -*- coding: utf-8 -*-
"""Inspect verification_evidence rows in full."""
import sqlite3, json

con = sqlite3.connect('/root/.hermes/profiles/408-study/verification_evidence.db')
cur = con.cursor()
print('=== verification_events (all) ===')
cur.execute('SELECT * FROM verification_events')
cols = [d[0] for d in cur.description]
print('cols:', cols)
for r in cur.fetchall():
    for c, v in zip(cols, r):
        print(' ', c, '=', str(v)[:300])
    print('---')
print('=== verification_state (all) ===')
cur.execute('SELECT * FROM verification_state')
cols = [d[0] for d in cur.description]
for r in cur.fetchall():
    print('===')
    for c, v in zip(cols, r):
        print(' ', c, '=', str(v)[:500])
print('=== meta ===')
cur.execute('SELECT * FROM meta')
for r in cur.fetchall():
    print(r)
con.close()
