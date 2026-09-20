# -*- coding: utf-8 -*-
"""W38 正式版复盘 · 采集 #3：gateway.log 投递尝试统计 + cron jobs.json prompt 检查（只读）"""
import json
import re
import os
from collections import Counter, defaultdict

LOG = '/root/.hermes/profiles/408-study/logs/gateway.log'
JOBS = '/root/.hermes/profiles/408-study/cron/jobs.json'

print('=== gateway.log ===')
print('size bytes:', os.path.getsize(LOG))
lines = open(LOG, encoding='utf-8', errors='replace').read().splitlines()
print('lines:', len(lines))
print('first:', lines[0][:120] if lines else '')
print('last :', lines[-1][:120] if lines else '')

byday = defaultdict(Counter)
pat_day = re.compile(r'(2026-\d\d-\d\d)')
for ln in lines:
    m = pat_day.search(ln)
    d = m.group(1) if m else ('2026-09-20' if 'no-date' else '?')
    low = ln.lower()
    if 'rate limited' in low and 'cooldown' in low:
        byday[d]['cooldown-rate-limited'] += 1
    if 'prepare failed' in low:
        byday[d]['prepare-failed'] += 1
    if 'sendmessage' in low:
        byday[d]['sendmessage-mention'] += 1
    if 'send failed' in low:
        byday[d]['send-failed'] += 1

print('\n--- 按日期（gateway.log 内出现日期串的行）---')
for d in sorted(byday):
    if d >= '2026-09-10':
        print('  %s %s' % (d, dict(byday[d])))

print('\n--- 不按日期，按正则匹配失败签名总数 ---')
c = Counter()
for ln in lines:
    if 'prepare failed' in ln:
        c['prepare failed'] += 1
    if 'rate limited' in ln:
        c['rate limited'] += 1
    if 'Weixin send failed' in ln:
        c['Weixin send failed'] += 1
    if 'live adapter send failed' in ln:
        c['live adapter send failed'] += 1
print(' ', dict(c))

print('\n--- 最后 8 行（原始）---')
for ln in lines[-8:]:
    print('  ', ln[:220])

print('\n\n=== cron jobs.json ===')
jb = json.load(open(JOBS, encoding='utf-8'))
jobs = jb if isinstance(jb, list) else jb.get('jobs', jb)
if isinstance(jobs, dict):
    items = list(jobs.items())
else:
    items = [(j.get('id'), j) for j in jobs]
for jid, j in items:
    if not isinstance(j, dict):
        continue
    name = j.get('name', '?')
    print('\n--- %s | %s ---' % (jid, name))
    for k in ['schedule', 'deliver', 'enabled', 'state', 'script', 'mode',
              'last_run', 'last_status', 'next_run', 'paused']:
        if k in j:
            print('   %s = %s' % (k, str(j[k])[:120]))
    p = j.get('prompt') or ''
    print('   prompt len =', len(p))
    for kw in ['ilink-diag', '探测', 'probe', 'send-only', 'ilink-diag.log']:
        if kw in p:
            print('   >> prompt 含关键词: %s' % kw)
    print('   prompt head:', p[:200].replace('\n', ' '))
