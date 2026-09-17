#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""W38 周复盘落盘校验（只读）。用法: python3 review-w38-verify.py"""
import json
import os
import sys

BASE = "/Users/liqin/Projects/AI-Study"
checks = []


def ck(name, cond, detail=""):
    checks.append((name, bool(cond), detail))


# 1. 周报存在
p = os.path.join(BASE, "总结/每周/2026-W38.md")
ck("W38 周报存在", os.path.isfile(p),
   "%d bytes" % (os.path.getsize(p) if os.path.isfile(p) else 0))

# 2. changelog 含 W38 行
cl = open(os.path.join(BASE, "状态数据/roadmap-changelog.md"), encoding="utf-8").read()
ck("changelog 含 W38 补跑版行", "2026-W38 补跑版" in cl)

# 3. system-state
st = json.load(open(os.path.join(BASE, "状态数据/system-state.json"), encoding="utf-8"))
ck("system-state current_day == 48", st["current_project"]["current_day"] == 48,
   str(st["current_project"]["current_day"]))
ck("system-state today_session.date == 2026-09-17",
   st["today_session"]["date"] == "2026-09-17")

# 4. dashboard
d = json.load(open(os.path.join(BASE, "状态数据/dashboard-data.json"), encoding="utf-8"))
ck("dashboard current_day == 48", d["progress"]["current_day"] == 48,
   str(d["progress"]["current_day"]))
ck("dashboard days_remaining == 100", d["progress"]["days_remaining"] == 100,
   str(d["progress"]["days_remaining"]))
ck("dashboard overdue == 139", d["tasks"]["overdue_tasks"] == 139,
   str(d["tasks"]["overdue_tasks"]))

# 5. diag log 含 9/17 行
dl = open(os.path.join(BASE, "scripts/ilink-diag.log"), encoding="utf-8").read()
ck("ilink-diag.log 含 9/17 探测行", "2026-09-17 12:13" in dl)

ok = all(c[1] for c in checks)
for n, c, det in checks:
    print(("PASS" if c else "FAIL"), "-", n, ("(" + det + ")" if det else ""))
print("RESULT:", "ALL PASS" if ok else "HAS FAILURES")
sys.exit(0 if ok else 1)
