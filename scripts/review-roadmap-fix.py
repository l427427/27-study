#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-W32 周复盘：roadmap.json 数据校准（原子写入）
- phase-1 → closed, phase-2 → active
- phase-2 goal 408 目标修正
- 408 任务编号自第6讲全量续排
"""
import json, os

P = '/root/27-study/状态数据/roadmap.json'

with open(P, encoding='utf-8') as f:
    rm = json.load(f)

# 1) 阶段状态切换
for ph in rm['phases']:
    if ph['id'] == 'phase-1':
        ph['status'] = 'closed'
    elif ph['id'] == 'phase-2':
        ph['status'] = 'active'
        ph['goal'] = '完成高数8讲+线代4讲+英语小三门3讲；数据结构自第6讲续推（每天2讲），8/27 前推进至~第52讲'

# 2) 408 任务编号校准（自第6讲续排，每天2讲）
title_map = {
    't045': '408 DS：王道视频第9-11讲 + 课后选择题',
    't051': '408 DS：王道视频第12-14讲 + 课后选择题',
    't056': '408 DS：王道视频第15-16讲',
    't059': '408 DS：王道视频第17-18讲',
    't062': '408 DS：王道视频第19-20讲',
    't065': '408 DS：王道视频第21-22讲',
    't068': '408 DS：王道视频第23-24讲',
    't071': '408 DS：王道视频第25-26讲',
    't074': '408 DS：王道视频第27-28讲',
    't077': '408 DS：王道视频第29-30讲',
    't080': '408 DS：王道视频第31-32讲',
    't083': '408 DS：王道视频第33-34讲',
    't086': '408 DS：王道视频第35-36讲',
    't089': '408 DS：王道视频第37-38讲',
    't092': '408 DS：王道视频第39-40讲',
    't095': '408 DS：王道视频第41-42讲',
    't098': '408 DS：王道视频第43-44讲',
    't101': '408 DS：王道视频第45-46讲',
    't104': '408 DS：王道视频第47-48讲',
    't107': '408 DS：王道视频第49-50讲',
    't111': '408 DS：王道视频第51-52讲',
}
REASON = '2026-08-09 周复盘校准：8/6 用户告知王道实际进度为第5讲，任务编号自第6讲续排'
changed = 0
for t in rm['tasks']:
    tid = t['id']
    if tid in title_map:
        t['title'] = title_map[tid]
        t['adjustment_reason'] = REASON
        changed += 1

# 3) metadata 记录
rm.setdefault('metadata', {})['last_review'] = '2026-08-09: 2026-W32 周复盘（phase切换 + 408编号全量校准）'

tmp = P + '.tmp'
with open(tmp, 'w', encoding='utf-8') as f:
    json.dump(rm, f, ensure_ascii=False)
os.replace(tmp, P)

# 验证
with open(P, encoding='utf-8') as f:
    rm2 = json.load(f)
print('tasks changed:', changed)
print('phases:', [(x['id'], x['status']) for x in rm2['phases']])
print('phase2 goal:', [x['goal'] for x in rm2['phases'] if x['id'] == 'phase-2'][0])
print('t045:', [t['title'] for t in rm2['tasks'] if t['id'] == 't045'][0])
print('t056:', [t['title'] for t in rm2['tasks'] if t['id'] == 't056'][0])
print('t111:', [t['title'] for t in rm2['tasks'] if t['id'] == 't111'][0])
print('metadata:', rm2.get('metadata'))
