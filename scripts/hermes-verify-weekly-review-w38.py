#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""W38 正式版周复盘 · 落盘校验（ad-hoc，非正式测试套件）。
用法: python3 hermes-verify-weekly-review-w38.py
覆盖：周报落盘 / 补跑版留档 / changelog / system-state / dashboard / roadmap 重数 /
      ilink 探测日志 / 新脚本存在与分支 / 备份脚本修复 / git 推送 / 无伪造记录
"""
import json
import os
import subprocess
import sys

BASE = "/root/27-study"
SD = os.path.join(BASE, "状态数据")
SC = os.path.join(BASE, "scripts")
WEEK = os.path.join(BASE, "总结/每周")
checks = []


def ck(name, cond, detail=""):
    checks.append((name, bool(cond), detail))


def rd(p):
    return open(p, encoding="utf-8").read()


# ---------- 1. 周报落盘 + 补跑版留档 ----------
p_off = os.path.join(WEEK, "2026-W38.md")
p_mk = os.path.join(WEEK, "2026-W38-补跑版-20260917.md")
ck("W38 正式版存在", os.path.isfile(p_off),
   "%d bytes" % (os.path.getsize(p_off) if os.path.isfile(p_off) else 0))
ck("9/17 补跑版已留档", os.path.isfile(p_mk),
   "%d bytes" % (os.path.getsize(p_mk) if os.path.isfile(p_mk) else 0))
off = rd(p_off) if os.path.isfile(p_off) else ""
ck("正式版标题含「正式版」", "W38 周复盘（正式版" in off)
ck("正式版覆盖 9/14–9/20", "9/14–9/20" in off)
ck("正式版含 8 个章节", off.count("\n## ") >= 8, "## 数=%d" % off.count("\n## "))
for kw in ["计划 vs 实际完成", "学习模式识别", "下周建议", "高频错题"]:
    ck("正式版含小节关键词: %s" % kw, kw in off)
ck("正式版写明备份链故障+修复", "pathspec" in off and "sync-study.sh" in off)
ck("正式版写明探测断点修复", "9/18、9/19" in off or "9/18、9/19 漏测" in off)
ck("正式版未伪造完成数", "completed=0" in off or "0 / 21" in off)
ck("正式版含交付说明(may fail)", "大概率发不出去" in off)

# ---------- 2. changelog ----------
cl = rd(os.path.join(SD, "roadmap-changelog.md"))
ck("changelog 含 W38 正式版行", "2026-09-20 10:05" in cl and "正式版" in cl)
ck("changelog 记录了备份链根因", "pathspec" in cl)

# ---------- 3. system-state ----------
st = json.load(open(os.path.join(SD, "system-state.json"), encoding="utf-8"))
ck("system-state current_day == 51", st["current_project"]["current_day"] == 51,
   str(st["current_project"]["current_day"]))
ck("system-state today_session.date == 2026-09-20",
   st["today_session"]["date"] == "2026-09-20", st["today_session"]["date"])
ck("system-state status == day_closed", st["current_status"] == "day_closed",
   st["current_status"])
ck("system-state last_session 未伪造(仍 no_report)",
   st["last_session"]["status"] == "no_report", st["last_session"]["status"])

# ---------- 4. dashboard ----------
d = json.load(open(os.path.join(SD, "dashboard-data.json"), encoding="utf-8"))
ck("dashboard current_day == 51", d["progress"]["current_day"] == 51,
   str(d["progress"]["current_day"]))
ck("dashboard days_remaining == 97", d["progress"]["days_remaining"] == 97,
   str(d["progress"]["days_remaining"]))
ck("dashboard overdue == 148", d["tasks"]["overdue_tasks"] == 148,
   str(d["tasks"]["overdue_tasks"]))
ck("dashboard completed == 0（未伪造）", d["tasks"]["completed_tasks"] == 0)
ck("dashboard total == 205", d["tasks"]["total_tasks"] == 205)

# ---------- 5. roadmap 独立重数 ----------
rm = json.load(open(os.path.join(SD, "roadmap.json"), encoding="utf-8"))
ts = rm["tasks"]
ck("roadmap 任务总数 == 205", len(ts) == 205, str(len(ts)))
ck("roadmap completed == 0（未伪造）",
   sum(1 for t in ts if t.get("status") == "completed") == 0)
od = [t for t in ts if t.get("date", "") < "2026-09-20"
      and t.get("status") != "completed" and not t.get("archived")]
ck("逾期重数 == 148（排除 archived）", len(od) == 148, str(len(od)))
ck("归档 == 24", sum(1 for t in ts if t.get("archived")) == 24)
win = [t for t in ts if "2026-09-14" <= t.get("date", "") <= "2026-09-20"]
ck("W38 窗口任务 == 21 项", len(win) == 21, str(len(win)))
ck("W38 窗口全部未完成", all(t.get("status") != "completed" for t in win))
ck("W38 窗口每日 3 项", len(set(t["date"] for t in win)) == 7
   and all(sum(1 for t in win if t["date"] == dd) == 3 for dd in set(t["date"] for t in win)))
ck("roadmap 408 链尾部到 9/30", any(t["id"] == "t203" and t["date"] == "2026-09-30"
                                    for t in ts))
# 编号连续性（按「有意重启」分段检查：8/6 校准 + phase-3 保守重排 —— 两处均在 changelog 有记录。
# 全链直接做全局单调断言会误报，见 W35/W38 教训：先怀疑断言口径，再动数据）
import re
nums = []
for t in sorted([x for x in ts if x.get("subject") == "408" and not x.get("archived")],
                key=lambda x: x["id"]):
    m = re.search(r"第(\d+)-(\d+)讲", t.get("title") or "")
    if m:
        nums.append((int(m.group(1)), int(m.group(2))))
runs = [[nums[0]]]
for i in range(1, len(nums)):
    if nums[i][0] == runs[-1][-1][1] + 1:
        runs[-1].append(nums[i])
    else:
        runs.append([nums[i]])
ck("408 讲次：每段内部连续（无空洞）",
   all(all(r[i][0] == r[i - 1][1] + 1 for i in range(1, len(r))) for r in runs),
   "段数=%d 段首=%s" % (len(runs), [r[0][0] for r in runs]))
ck("408 讲次：仅 2 处有意重启且均回到第 6 讲",
   [r[0][0] for r in runs[1:]] == [6, 6], str([r[0][0] for r in runs[1:]]))
ck("408 讲次：末段连续到第 98 讲", runs[-1][-1][1] == 98, str(runs[-1][-1]))

# ---------- 6. 探测日志 ----------
dl = rd(os.path.join(SC, "ilink-diag.log"))
ck("ilink-diag.log 含 9/20 探测行", "2026-09-20 10:02" in dl)
ck("9/20 探测记录 prepare failed/未恢复", "prepare failed" in dl.split("2026-09-20")[-1])

# ---------- 7. 新脚本 + 分支 ----------
for f in ["ilink-probe-log.py", "ilink-probe-log-selftest.py",
          "review-w38-official-calibrate.py", "review-w38-official-collect.py",
          "review-w38-official-state.py"]:
    ck("脚本存在: %s" % f, os.path.isfile(os.path.join(SC, f)))

# ---------- 8. 备份脚本修复（两处副本） ----------
for p in ["/root/.hermes/profiles/408-study/scripts/sync-study.sh",
          "/root/.hermes/scripts/sync-study.sh"]:
    src = rd(p)
    ck("备份脚本改引号消息: %s" % p.split("/")[3],
       'git commit -m "自动备份 $(date' in src)
    ck("备份脚本无写死日期 2026-08-03: %s" % p.split("/")[3], "2026-08-03" not in src)
    ck("备份脚本 commit 失败 exit 1: %s" % p.split("/")[3],
       "备份失败: git commit" in src)
    r = subprocess.run(["bash", "-n", p], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    ck("备份脚本语法 OK: %s" % p.split("/")[3], r.returncode == 0)

# ---------- 9. git 推送 ----------
r = subprocess.run(["git", "-C", BASE, "log", "--oneline", "-1"],
                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
head = r.stdout.decode("utf-8", "replace").strip()
ck("git 最新提交为 9/20 自动备份", "2026-09-20" in head, head[:60])
r = subprocess.run(["git", "-C", BASE, "rev-parse", "HEAD", "origin/main"],
                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
sha = r.stdout.decode("utf-8", "replace").split()
ck("本地 HEAD == origin/main（已推送）", len(sha) == 2 and sha[0] == sha[1], " ".join(sha)[:80])
r = subprocess.run(["git", "-C", BASE, "show", "--name-only", "--pretty=format:", "HEAD"],
                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
files = r.stdout.decode("utf-8", "replace")
ck("HEAD 提交包含 W38 周报", "2026-W38.md" in files)
ck("HEAD 提交包含 changelog", "roadmap-changelog.md" in files)

# ---------- 10. 无伪造记录 ----------
ck("每日记录无新增 md（不补写缺勤）",
   not any(f.endswith(".md") for f in os.listdir(os.path.join(BASE, "每日记录"))))
ck("错题本仍为空（不编造错题）",
   not any(f.endswith(".md") for f in os.listdir(os.path.join(BASE, "错题本"))))
ma = json.load(open(os.path.join(SD, "mastery.json"), encoding="utf-8"))
ck("mastery 未编造掌握度", ma.get("topics") == {}, json.dumps(ma.get("topics"))[:40])

ok = all(c[1] for c in checks)
for n, c, det in checks:
    print(("PASS" if c else "FAIL"), "-", n, ("(" + det + ")" if det else ""))
print("TOTAL: %d checks, %s" % (len(checks), "ALL PASS" if ok else "HAS FAILURES"))
sys.exit(0 if ok else 1)
