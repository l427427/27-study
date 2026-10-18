# -*- coding: utf-8 -*-
"""W42: 提取 cron 归档「最后一次 ## Response」正文头部 + 判断 [SILENT]；并抓 gateway.log 全 [Weixin] 行"""
import os, re, glob

OUT = '/root/.hermes/profiles/408-study/cron/output'
JOBS = {'0d34337730f8': '早班09:00', '55bd60a924fd': '晚班21:00'}

for jid, name in JOBS.items():
    print('=' * 18, name, jid)
    for f in sorted(glob.glob(os.path.join(OUT, jid, '2026-10-1[2-8]*.md'))):
        base = os.path.basename(f)
        txt = open(f, encoding='utf-8').read()
        header = txt.split('\n', 1)[0]
        idx = txt.rfind('## Response')
        body = txt[idx + len('## Response'):].strip() if idx >= 0 else ''
        silent = body.strip() in ('[SILENT]', '`[SILENT]`')
        print('\n--- %s | FAILED=%s | silent=%s | body_chars=%d' % (base, '(FAILED)' in header, silent, len(body)))
        print(body[:320].replace('\n', ' ⏎ '))
        print(' ...TAIL:', body[-160:].replace('\n', ' ⏎ ') if body else '')

print('\n' + '=' * 18, 'gateway.log 本周全部 [Weixin] 行')
gw = '/root/.hermes/profiles/408-study/logs/gateway.log'
for line in open(gw, encoding='utf-8', errors='replace'):
    if '[Weixin]' in line and re.match(r'2026-10-1[2-8]', line):
        print(line.rstrip()[:190])
