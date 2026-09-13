# -*- coding: utf-8 -*-
"""W37 collector #4: 9/10 09:00 cron 会话内容 + 9/11-9/13 提醒会话摘要（只读）。"""
import sqlite3

DB = '/root/.hermes/profiles/408-study/state.db'
con = sqlite3.connect(DB)
cur = con.cursor()

for sid in ['cron_0d34337730f8_20260910_090026',
            'cron_55bd60a924fd_20260911_210052',
            'cron_0d34337730f8_20260912_090001',
            'cron_0d34337730f8_20260913_090016']:
    print('=' * 70)
    print('SESSION', sid)
    print('=' * 70)
    cur.execute("""SELECT role, datetime(timestamp,'unixepoch','localtime'), substr(replace(content,char(10),' / '),1,260)
                   FROM messages WHERE session_id=? ORDER BY timestamp""", (sid,))
    for r in cur.fetchall():
        print(' [%s] %-9s %s' % (r[1], r[0], r[2]))
    print()
con.close()
