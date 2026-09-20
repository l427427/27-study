# -*- coding: utf-8 -*-
"""W38 正式版复盘 · 采集 #2：state.db 真人入站时间线 + 投递义务（只读）"""
import sqlite3
import datetime

DB = '/root/.hermes/profiles/408-study/state.db'
con = sqlite3.connect('file:%s?mode=ro' % DB, uri=True)
cur = con.cursor()


def fmt(ts):
    try:
        return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')
    except Exception:
        return str(ts)


mcols = [r[1] for r in cur.execute('PRAGMA table_info(messages)')]
print('messages columns:', mcols)
sess_col = 'session_id' if 'session_id' in mcols else ('session_key' if 'session_key' in mcols else None)
print('session link column =', sess_col)

print('\n=== A. 近期消息（join sessions，看归属）===')
q = """select m.id, m.timestamp, m.role, s.source, s.id,
              substr(replace(m.content, char(10), ' '), 1, 130)
       from messages m left join sessions s on m.%s = s.id
       where m.timestamp > strftime('%%s','2026-09-13')
       order by m.timestamp desc limit 25""" % sess_col
for r in cur.execute(q):
    print('  %s | %s | %-9s | src=%-7s | %s' % (r[0], fmt(r[1]), r[2], r[3], r[5]))

print('\n=== B. 分来源计数（9/13 之后）===')
q = """select case when m.content like '[IMPORTANT%%' then 'cron-self-prompt'
                   when m.role='user' then 'human-user'
                   else m.role end as kind,
              coalesce(s.source,'(no-session)'), count(*)
       from messages m left join sessions s on m.%s = s.id
       where m.timestamp > strftime('%%s','2026-09-13')
       group by kind, s.source order by 3 desc""" % sess_col
for r in cur.execute(q):
    print('  %-18s src=%-10s n=%s' % (r[0], r[1], r[2]))

print('\n=== C. 真人入站（排除 cron 自触发 prompt）===')
q = """select m.id, m.timestamp, coalesce(s.source,'?'),
              substr(replace(m.content, char(10), ' '), 1, 160)
       from messages m left join sessions s on m.%s = s.id
       where m.role='user' and m.content not like '[IMPORTANT%%'
         and m.timestamp > strftime('%%s','2026-08-25')
       order by m.timestamp desc limit 20""" % sess_col
rows = list(cur.execute(q))
if not rows:
    print('  (无)')
for r in rows:
    print('  %s | %s | src=%s | %s' % (r[0], fmt(r[1]), r[2], r[3]))

print('\n=== D. delivery_obligations 状态分布 ===')
for r in cur.execute('select state, count(*) from delivery_obligations group by state order by 2 desc'):
    print('  %-12s %s' % (r[0], r[1]))

print('\n=== E. delivery_obligations 最近 12 条 ===')
q = """select obligation_id, platform, state, attempts, created_at, updated_at, last_error
       from delivery_obligations order by updated_at desc limit 12"""
for r in cur.execute(q):
    print('  %s | %s | %s | att=%s | created=%s | updated=%s\n      err=%s' % (
        r[0][:18], r[1], r[2], r[3], fmt(r[4]), fmt(r[5]),
        (r[6] or '')[:150]))

print('\n=== F. weixin 会话（近期）===')
q = """select id, source, started_at, ended_at, message_count, title,
              last_activity_at, last_activity_description
       from sessions where source='weixin' order by started_at desc limit 10"""
for r in cur.execute(q):
    print('  %s | %s | start=%s | msgs=%s | %s | last=%s (%s)' % (
        r[0][:20], r[1], fmt(r[2]), r[4], (r[5] or '')[:34], fmt(r[6]),
        (r[7] or '')[:40]))

print('\n=== G. 全部会话来源分布（9/10 起）===')
q = """select source, count(*), min(started_at), max(started_at)
       from sessions where started_at > strftime('%s','2026-09-10')
       group by source order by 2 desc"""
for r in cur.execute(q):
    print('  %-12s n=%s | %s .. %s' % (r[0], r[1], fmt(r[2]), fmt(r[3])))

con.close()
