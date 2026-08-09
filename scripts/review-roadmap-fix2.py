#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Backfill t039 adjustment_reason (8/6 calibration was title-only)."""
import json, os

P = '/root/27-study/状态数据/roadmap.json'
with open(P, encoding='utf-8') as f:
    rm = json.load(f)

for t in rm['tasks']:
    if t['id'] == 't039':
        t['adjustment_reason'] = '2026-08-06 408进度校准：用户告知王道实际进度为第5讲，任务改为第6-8讲'

tmp = P + '.tmp'
with open(tmp, 'w', encoding='utf-8') as f:
    json.dump(rm, f, ensure_ascii=False)
os.replace(tmp, P)

with open(P, encoding='utf-8') as f:
    rm2 = json.load(f)
print('t039 reason:', [t['adjustment_reason'] for t in rm2['tasks'] if t['id'] == 't039'][0])
