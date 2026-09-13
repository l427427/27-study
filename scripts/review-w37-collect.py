#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-W37 周复盘数据采集（9/7-9/13）。只读，不改数据。

采集：① state.db 入站用户消息时间线（全来源）② delivery_obligations 失败证据
③ 各 session source 分布 ④ 27-study 近期文件变动
"""
import os, sqlite3, subprocess, sys

STATE_DB = '/root/.hermes/profiles/408-study/state.db'


def q(sql, args=()):
    con = sqlite3.connect('file:%s?mode=ro' % STATE_DB, uri=True)
    con.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in con.execute(sql, args).fetchall()]
    except Exception as e:
        print('SQL ERR:', e, '\n  sql=', sql)
        return []
    finally:
        con.close()


print('=' * 70)
print('1) state.db 表结构')
print('=' * 70)
for r in q("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
    print(' -', r['name'])

print()
print('=' * 70)
print('2) sessions 按 source 汇总（最近）')
print('=' * 70)
for r in q("SELECT source, COUNT(*) n, MAX(created_at) last FROM sessions GROUP BY source ORDER BY last DESC"):
    print('  %-12s n=%-5s last=%s' % (r['source'], r['n'], r['last']))

print()
print('=' * 70)
print('3) 全部 role=user 消息（按时间倒序，取最近 30 条）——人类互动时间线')
print('=' * 70)
rows = q("""SELECT m.id, m.session_id, m.role, m.created_at, substr(m.content,1,300) c,
                   s.source
            FROM messages m LEFT JOIN sessions s ON s.session_id = m.session_id
            WHERE m.role='user'
            ORDER BY m.created_at DESC LIMIT 30""")
if not rows:
    rows = q("""SELECT id, session_id, role, created_at, substr(content,1,300) c,
                        NULL as source FROM messages WHERE role='user'
                ORDER BY created_at DESC LIMIT 30""")
for r in rows:
    print('  [%s] %s src=%s' % (r['created_at'], (r['c'] or '').replace('\n', ' / '), r.get('source')))

print()
print('=' * 70)
print('4) 9/6 之后的用户消息（本周窗口）')
print('=' * 70)
for r in q("""SELECT m.id, m.created_at, substr(m.content,1,500) c, s.source
              FROM messages m LEFT JOIN sessions s ON s.session_id=m.session_id
              WHERE m.role='user' AND m.created_at >= '2026-09-06'
              ORDER BY m.created_at"""):
    print('  [%s] src=%s :: %s' % (r['created_at'], r.get('source'), (r['c'] or '').replace('\n', ' / ')))

print()
print('=' * 70)
print('5) delivery_obligations 9/6 起')
print('=' * 70)
try:
    for r in q("SELECT * FROM delivery_obligations WHERE created_at >= '2026-09-06' ORDER BY created_at LIMIT 40"):
        print('  ', {k: (str(v)[:120] if v is not None else None) for k, v in r.items()})
except Exception as e:
    print('  err', e)

print()
print('=' * 70)
print('6) delivery_obligations 状态汇总')
print('=' * 70)
try:
    for r in q("SELECT status, COUNT(*) n, MIN(created_at) f, MAX(created_at) l FROM delivery_obligations GROUP BY status"):
        print('  %-12s n=%-5s %s .. %s' % (r['status'], r['n'], r['f'], r['l']))
except Exception as e:
    print('  err', e)

print()
print('=' * 70)
print('7) sessions 9/6 起（cron 运行痕迹）')
print('=' * 70)
try:
    for r in q("""SELECT session_id, source, substr(title,1,60) t, created_at
                  FROM sessions WHERE created_at >= '2026-09-06' ORDER BY created_at"""):
        print('  [%s] %-10s %s' % (r['created_at'], r['source'], r['t']))
except Exception as e:
    print('  err', e)

print()
print('=' * 70)
print('8) cron job 运行结果 (executions.db 若有)')
print('=' * 70)
for p in ['/root/.hermes/profiles/408-study/executions.db']:
    print('  exists %s = %s' % (p, os.path.exists(p)))
