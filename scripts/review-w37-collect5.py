# -*- coding: utf-8 -*-
"""W37 collector #5: 本周投递失败量化（gateway.log 按天）+ cron executions 统计。只读。"""
import re, sqlite3, os
from collections import Counter

LOG = '/root/.hermes/profiles/408-study/logs/gateway.log'
print('=== gateway.log weixin 发送失败按天（8/28 起）===')
cnt = Counter()
other = Counter()
try:
    with open(LOG, encoding='utf-8', errors='replace') as f:
        for line in f:
            if 'iLink sendmessage' not in line and 'send failed' not in line:
                continue
            m = re.match(r'^(\d{4}-\d{2}-\d{2}) (\d{2})', line)
            if not m:
                continue
            if m.group(1) < '2026-08-28':
                continue
            cnt[m.group(1)] += 1
            other[m.group(1) + ' ' + m.group(2) + '时'] += 1
except Exception as e:
    print('  err', e)
for d in sorted(cnt):
    print('  %s  %d' % (d, cnt[d]))
print('  合计:', sum(cnt.values()))
print('  按小时（9/7 起）:')
for k in sorted(other):
    if k >= '2026-09-07':
        print('   ', k, other[k])

print('\n=== gateway.log inbound 入站记录（8/28 起）===')
try:
    with open(LOG, encoding='utf-8', errors='replace') as f:
        for line in f:
            if 'inbound' in line and line[:10] >= '2026-08-28':
                print('  ', line.rstrip()[:180])
except Exception as e:
    print('  err', e)

print('\n=== gateway.log weixin 连接/断开事件（8/28 起）===')
try:
    with open(LOG, encoding='utf-8', errors='replace') as f:
        for line in f:
            if ('weixin connected' in line or 'disconnect' in line.lower() or 'reconnect' in line.lower()) and line[:10] >= '2026-08-28':
                print('  ', line.rstrip()[:180])
except Exception as e:
    print('  err', e)

print('\n=== cron executions 9/7 起（按 job）===')
p = '/root/.hermes/profiles/408-study/cron/executions.db'
print('  exists', p, os.path.exists(p))
if os.path.exists(p):
    con = sqlite3.connect('file:%s?mode=ro' % p, uri=True)
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print('  tables:', [r[0] for r in cur.fetchall()])
    try:
        cur.execute("SELECT job_id, COUNT(*), datetime(MIN(started_at),'unixepoch','localtime'), datetime(MAX(started_at),'unixepoch','localtime') FROM executions WHERE started_at >= strftime('%s','2026-09-07 00:00:00','utc') GROUP BY job_id")
        for r in cur.fetchall():
            print('  ', r)
    except Exception as e:
        print('  err', e)
    con.close()
