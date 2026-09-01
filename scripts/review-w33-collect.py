#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-W33 周复盘数据收集：解析 roadmap.json（单行大JSON）+ 汇总任务状态"""
import json, sys

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

rm = load_json('/root/27-study/状态数据/roadmap.json')
print("=== roadmap.json top keys ===")
print(list(rm.keys()))

# 找出任务列表所在位置
tasks = None
phases = None
for k, v in rm.items():
    if isinstance(v, list) and v and isinstance(v[0], dict) and 'id' in v[0]:
        tasks = v
    if isinstance(v, dict) and 'phases' in str(v.get('phase-1', ''))[:0] or k == 'phases':
        phases = v
    if isinstance(v, dict) and 'phase-1' in v:
        phases = v

if tasks is None:
    # 递归找
    def find_tasks(obj):
        if isinstance(obj, list) and obj and isinstance(obj[0], dict) and 'id' in obj[0]:
            return obj
        if isinstance(obj, dict):
            for v in obj.values():
                r = find_tasks(v)
                if r: return r
        return None
    tasks = find_tasks(rm)

print(f"\n=== tasks: {len(tasks) if tasks else 0} 个 ===")
if tasks:
    print("task keys:", list(tasks[0].keys()))

# 统计
from collections import Counter, defaultdict
if tasks:
    status_c = Counter(t.get('status') for t in tasks)
    print("status 分布:", dict(status_c))
    subj_c = Counter(t.get('subject', '?') for t in tasks)
    print("科目分布:", dict(subj_c))
    # 未完成任务按日期分组
    pending = [t for t in tasks if t.get('status') != 'completed']
    by_date = defaultdict(list)
    for t in pending:
        d = t.get('date', t.get('planned_date', '?'))
        by_date[d].append(t.get('id'))
    print("\n未完成任务按日期:")
    for d in sorted(by_date.keys()):
        print(f"  {d}: {len(by_date[d])} 个 -> {by_date[d][:8]}{'...' if len(by_date[d])>8 else ''}")
    # 8/9 之后的任务（本周 8/10-8/16 应为 8/9-8/27 集训期任务）
    print("\n=== 8/9 - 8/27 (phase-2 集训期) 任务 ===")
    for t in pending:
        d = t.get('date', t.get('planned_date', ''))
        if isinstance(d, str) and ('08-' in d):
            day = d.split('-')[-1]
            try:
                if 9 <= int(day) <= 27:
                    print(f"  {t.get('id')} | {d} | {t.get('subject')} | {t.get('title','')[:40]} | {t.get('status')} | planned={t.get('planned_minutes')} actual={t.get('actual_minutes')}")
            except ValueError:
                pass
    # 科目与阶段结构
print("\n=== phases 结构 ===")
if 'phases' in rm:
    print(json.dumps(rm['phases'], ensure_ascii=False, indent=1)[:2500])
elif phases:
    print(json.dumps(phases, ensure_ascii=False, indent=1)[:2500])
