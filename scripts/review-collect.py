#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""周复盘数据采集：解析 roadmap.json 与 dashboard-data.json"""
import json, sys

def load(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)

rm = load('/root/27-study/状态数据/roadmap.json')
print("=== ROADMAP SUMMARY ===")
print("title:", rm.get("title"))
print("goal:", rm.get("goal", {}).get("statement"))
print("\n--- Phases ---")
for p in rm.get("phases", []):
    print(f"[{p.get('id')}] {p.get('title')} | {p.get('date_range')} | {p.get('days')}天 | status={p.get('status')}")
    print(f"    goal: {p.get('goal')}")

print("\n--- Tasks (all phases) ---")
for p in rm.get("phases", []):
    for t in p.get("tasks", []):
        print(f"  {t.get('id')} | {t.get('title')} | date={t.get('date')} | status={t.get('status')} | planned={t.get('planned_minutes')} | actual={t.get('actual_minutes')} | reason={t.get('reason','')}")

print("\n--- Phase-1 task keys ---")
if rm.get("phases"):
    print(list(rm["phases"][0].keys()))

print("\n--- Other top-level keys ---")
print(list(rm.keys()))

# dashboard-data
try:
    db = load('/root/27-study/状态数据/dashboard-data.json')
    print("\n=== DASHBOARD-DATA ===")
    print(json.dumps(db, ensure_ascii=False, indent=1)[:3000])
except Exception as e:
    print("dashboard read error:", e)

try:
    db2 = load('/root/27-study/dashboard-data.json')
    print("\n=== /root/27-study/dashboard-data.json ===")
    print(json.dumps(db2, ensure_ascii=False, indent=1)[:3000])
except Exception as e:
    print("dashboard2 read error:", e)
