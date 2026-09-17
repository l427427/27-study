#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""W38 复盘数据采集：roadmap 摘要（只读）"""
import json
import collections

P = "/Users/liqin/Projects/AI-Study/状态数据/roadmap.json"
d = json.load(open(P, encoding="utf-8"))
tasks = d["tasks"]
print("total tasks:", len(tasks))
print("status:", dict(collections.Counter(t.get("status") for t in tasks)))
print("archived(flag):", sum(1 for t in tasks if t.get("archived")))
print("sample keys:", sorted(tasks[100].keys()))
print("phases:", [(p["id"], p.get("status"), p.get("date_range")) for p in d.get("phases", [])])

p3 = [t for t in tasks if t.get("phase_id") == "phase-3"]
print("phase3 count:", len(p3), "status:", dict(collections.Counter(t.get("status") for t in p3)))

for day in ["2026-09-13", "2026-09-14", "2026-09-15", "2026-09-16", "2026-09-17",
            "2026-09-18", "2026-09-19", "2026-09-20", "2026-09-21"]:
    ds = [t for t in tasks if t.get("date") == day]
    print(day, "n=%d" % len(ds), "|", " ; ".join(
        "%s[%s]" % (t["id"], t.get("status")) for t in ds))

today = "2026-09-17"
od = [t for t in tasks if t.get("date") and t["date"] < today
      and t.get("status") != "completed" and not t.get("archived")]
print("overdue(date<today,not completed,not archived):", len(od))
print("overdue by phase:", dict(collections.Counter(t.get("phase_id") for t in od)))

for t in tasks:
    if t["id"] in ["t155", "t156", "t157", "t158", "t159", "t160", "t161", "t162",
                   "t163", "t164", "t165", "t166", "t167", "t168", "t169"]:
        print("detail", t["id"], t.get("date"), t.get("status"),
              t.get("title", "")[:44], t.get("estimated_minutes"))
