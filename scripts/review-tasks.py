#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""提取 roadmap.json 顶层 tasks 数组"""
import json

with open('/root/27-study/状态数据/roadmap.json', encoding='utf-8') as f:
    rm = json.load(f)

tasks = rm.get("tasks", [])
print("total tasks:", len(tasks))
print("\n--- All tasks ---")
for t in tasks:
    print(json.dumps(t, ensure_ascii=False))
