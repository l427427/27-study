# -*- coding: utf-8 -*-
"""W37 collector #2: state.db 入站/投递证据 + cron 执行库（只读）。"""
import sqlite3

DB = '/root/.hermes/profiles/408-study/state.db'
con = sqlite3.connect(DB)
cur = con.cursor()


def p(*a):
    print(*a)


p('=== sessions source counts ===')
cur.execute("SELECT source, COUNT(*), datetime(MAX(last_activity_at),'unixepoch','localtime') FROM sessions GROUP BY source")
for r in cur.fetchall():
    p('  ', r)

p('\n=== weixin sessions ===')
cur.execute("SELECT id, title, datetime(started_at,'unixepoch','localtime'), datetime(last_activity_at,'unixepoch','localtime'), message_count FROM sessions WHERE source='weixin' ORDER BY last_activity_at DESC LIMIT 10")
for r in cur.fetchall():
    p('  ', r)

p('\n=== 全部 role=user 消息（最近 20）===')
cur.execute("SELECT datetime(timestamp,'unixepoch','localtime') ts, substr(content,1,200) FROM messages WHERE role='user' ORDER BY timestamp DESC LIMIT 20")
for r in cur.fetchall():
    p('  ', r[0], '::', (r[1] or '').replace('\n', ' / '))

p('\n=== 用户消息按天统计（最近 30 天）===')
cur.execute("SELECT date(timestamp,'unixepoch','localtime') d, COUNT(*), group_concat(substr(content,1,40),' | ') FROM messages WHERE role='user' GROUP BY d ORDER BY d DESC LIMIT 30")
for r in cur.fetchall():
    p('  ', r)

p('\n=== 9/6 00:00 起的用户消息 ===')
cur.execute("SELECT datetime(timestamp,'unixepoch','localtime'), substr(content,1,300) FROM messages WHERE role='user' AND timestamp >= strftime('%s','2026-09-06 00:00:00','utc') ORDER BY timestamp")
rows = cur.fetchall()
p('  count =', len(rows))
for r in rows:
    p('  ', r[0], '::', (r[1] or '').replace('\n', ' / '))

p('\n=== 9/6 起 assistant 消息（系统回复尝试）===')
cur.execute("SELECT datetime(timestamp,'unixepoch','localtime'), substr(content,1,120) FROM messages WHERE role='assistant' AND timestamp >= strftime('%s','2026-09-06 00:00:00','utc') ORDER BY timestamp")
rows = cur.fetchall()
p('  count =', len(rows))
for r in rows[:40]:
    p('  ', r[0], '::', (r[1] or '').replace('\n', ' / '))

p('\n=== delivery_obligations schema ===')
cur.execute("SELECT sql FROM sqlite_master WHERE name='delivery_obligations'")
p('  ', cur.fetchone()[0])

p('\n=== delivery_obligations 按 state 汇总 ===')
cur.execute("SELECT state, COUNT(*), datetime(MIN(created_at),'unixepoch','localtime'), datetime(MAX(updated_at),'unixepoch','localtime') FROM delivery_obligations GROUP BY state")
for r in cur.fetchall():
    p('  ', r)

p('\n=== delivery_obligations 9/6 起逐日 ===')
cur.execute("SELECT date(updated_at,'unixepoch','localtime') d, state, COUNT(*) FROM delivery_obligations WHERE updated_at >= strftime('%s','2026-09-06 00:00:00','utc') GROUP BY d, state ORDER BY d")
for r in cur.fetchall():
    p('  ', r)

p('\n=== delivery_obligations 最近 15 ===')
cur.execute("SELECT obligation_id, state, attempts, datetime(created_at,'unixepoch','localtime'), datetime(updated_at,'unixepoch','localtime'), substr(content,1,60), substr(last_error,1,110) FROM delivery_obligations ORDER BY created_at DESC LIMIT 15")
for r in cur.fetchall():
    p('  ', r)

p('\n=== cron sessions 9/6 起（自动 job 运行痕迹）===')
cur.execute("SELECT id, source, substr(title,1,70), datetime(started_at,'unixepoch','localtime') FROM sessions WHERE started_at >= strftime('%s','2026-09-06 00:00:00','utc') ORDER BY started_at")
for r in cur.fetchall():
    p('  ', r)

p('\n=== cron/executions.db ===')
import os
for pth in ['/root/.hermes/profiles/408-study/cron/executions.db']:
    p('  exists', pth, os.path.exists(pth))
    if os.path.exists(pth):
        c2 = sqlite3.connect('file:%s?mode=ro' % pth, uri=True).cursor()
        c2.execute("SELECT sql FROM sqlite_master WHERE type='table'")
        p('  schema:', c2.fetchone()[0][:400])
con.close()
