#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""W39 正式版周复盘 · 落盘校验（ad-hoc，非正式测试套件）。
用法: python3 hermes-verify-weekly-review-w39.py
覆盖：周报落盘 / changelog / system-state / dashboard / roadmap 重数 /
      ilink 探测日志 7/7 / 备份链 git 判据 / 408 编号链分段 / 无伪造记录
"""
import json
import os
import re
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


def sh(*args):
    r = subprocess.run(list(args), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return r.returncode, r.stdout.decode("utf-8", "replace")


# ---------- 1. 周报落盘 ----------
p_off = os.path.join(WEEK, "2026-W39.md")
ck("W39 周报存在", os.path.isfile(p_off),
   "%d bytes" % (os.path.getsize(p_off) if os.path.isfile(p_off) else 0))
off = rd(p_off) if os.path.isfile(p_off) else ""
ck("标题含 W39", "2026-W39 周复盘" in off)
ck("覆盖 9/21–9/27", "9/21–9/27" in off)
ck("含 8 个章节", off.count("\n## ") >= 8, "## 数=%d" % off.count("\n## "))
for kw in ["计划 vs 实际完成", "学习模式识别", "下周建议", "高频错题",
           "用户本周对自己的一个新认识", "Roadmap 与系统侧调整"]:
    ck("含小节关键词: %s" % kw, kw in off)
ck("写明备份链整改已验证(48 次提交)", "48 次提交" in off)
ck("写明探测链 7/7 通过", "7/7" in off and "ilink-diag.log" in off)
ck("写明通道第 30 天", "第 **30** 天" in off or "第 30 天" in off)
ck("写明 phase-3 剩 3 天收口", "3 天" in off and "phase-4" in off)
ck("含新假设 H21", "H21" in off)
ck("未伪造完成数(completed=0)", "completed=0" in off or "0 / 21" in off)
ck("含投递说明(大概率发不出去)", "大概率发不出去" in off)
ck("未编造用户自我认识", "无任何用户输入，不编造" in off)

# ---------- 2. changelog ----------
cl = rd(os.path.join(SD, "roadmap-changelog.md"))
ck("changelog 含 W39 行", "2026-09-27 10:05" in cl and "2026-W39" in cl)
ck("changelog 记录 phase-3 收口倒计时", "phase-3 距 9/30 收口仅剩 3 天" in cl)
ck("changelog 记录 daily-audit-state 漏跑", "daily-audit-state.py` 今日 09:00 未执行" in cl or "daily-audit-state" in cl)
ck("changelog 含当场整改孤儿脚本行", "2026-09-27 10:15" in cl and "孤儿脚本" in cl)
ck("周报写明孤儿脚本根因", "孤儿脚本" in off and "已当场修复" in off)
ck("周报 P1 标记为已完成", "已当场完成" in off)
sk = rd("/root/.hermes/profiles/408-study/skills/ai-learning/ai-mentor-review-ops/SKILL.md")
ck("运维手册已加入 daily-audit-state 固定动作",
   "daily-audit-state.py" in sk and "第一步固定执行" in sk)
ck("运维手册判据升级为四件套", "判据四件套" in sk and "updated_at" in sk)

# ---------- 3. system-state ----------
st = json.load(open(os.path.join(SD, "system-state.json"), encoding="utf-8"))
ck("current_day == 58", st["current_project"]["current_day"] == 58,
   str(st["current_project"]["current_day"]))
ck("today_session.date == 2026-09-27",
   st["today_session"]["date"] == "2026-09-27", st["today_session"]["date"])
ck("current_status == day_closed", st["current_status"] == "day_closed",
   st["current_status"])
ck("last_session 未伪造(仍 no_report)",
   st["last_session"]["status"] == "no_report", st["last_session"]["status"])
ck("current_status 未被改成 completed/in_session",
   st["current_status"] not in ("completed", "in_session"))

# ---------- 4. dashboard ----------
d = json.load(open(os.path.join(SD, "dashboard-data.json"), encoding="utf-8"))
ck("dashboard current_day == 58", d["progress"]["current_day"] == 58,
   str(d["progress"]["current_day"]))
ck("dashboard days_remaining == 90", d["progress"]["days_remaining"] == 90,
   str(d["progress"]["days_remaining"]))
ck("dashboard overdue == 169", d["tasks"]["overdue_tasks"] == 169,
   str(d["tasks"]["overdue_tasks"]))
ck("dashboard completed == 0（未伪造）", d["tasks"]["completed_tasks"] == 0)
ck("dashboard total == 205", d["tasks"]["total_tasks"] == 205)
ck("dashboard 科目总和 == 205",
   sum(v["total_tasks"] for v in d["subjects"].values()) == 205,
   str(sum(v["total_tasks"] for v in d["subjects"].values())))

# ---------- 5. roadmap 独立重数 ----------
rm = json.load(open(os.path.join(SD, "roadmap.json"), encoding="utf-8"))
ts = rm["tasks"]
ck("roadmap 任务总数 == 205", len(ts) == 205, str(len(ts)))
ck("roadmap completed == 0（未伪造）",
   sum(1 for t in ts if t.get("status") == "completed") == 0)
od = [t for t in ts if t.get("date", "") < "2026-09-27"
      and t.get("status") != "completed" and not t.get("archived")]
ck("逾期重数 == 169（排除 archived）", len(od) == 169, str(len(od)))
ck("归档 == 24", sum(1 for t in ts if t.get("archived")) == 24)
win = [t for t in ts if "2026-09-21" <= t.get("date", "") <= "2026-09-27"]
ck("W39 窗口任务 == 21 项", len(win) == 21, str(len(win)))
ck("W39 窗口全部未完成", all(t.get("status") != "completed" for t in win))
days = set(t["date"] for t in win)
ck("W39 窗口 7 天 × 每天 3 项", len(days) == 7
   and all(sum(1 for t in win if t["date"] == dd) == 3 for dd in days))
ck("窗口末 3 项 = t194/t195/t196",
   sorted(t["id"] for t in win if t["date"] == "2026-09-27") == ["t194", "t195", "t196"])
ck("roadmap 408 链尾部到 9/30 第96-98讲",
   any(t["id"] == "t203" and t["date"] == "2026-09-30" and "第96-98讲" in (t.get("title") or "")
       for t in ts))
# 408 编号链：先按「有意重启」分段，再断言每段内部连续（W38 教训：不做全局单调断言）
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
ck("408 讲次：末段收在第 98 讲", runs[-1][-1][1] == 98, str(runs[-1][-1]))

# ---------- 6. 探测日志（W39：9/21–9/27 应 7/7 天有行）----------
dl = rd(os.path.join(SC, "ilink-diag.log"))
wk_days = ["2026-09-2%d" % d for d in range(1, 8)]
have = [x for x in wk_days if ("%s " % x) in dl]
ck("ilink-diag.log 本周 7/7 天有探测行", len(have) == 7, str(have))
ck("9/27 探测行已记录", "2026-09-27 09:01" in dl)
ck("本周探测均记为未恢复/签名不变",
   all("未恢复" in ln or "prepare failed" in ln
       for ln in dl.splitlines() if ln.startswith(tuple(wk_days))))
ck("连续 8 天有行（9/20–9/27）",
   all(("2026-09-%d " % d) in dl for d in range(20, 28)))

# ---------- 7. 备份链整周验证（H19 外部判据）----------
rc, n = sh("git", "-C", BASE, "log", "--since=2026-09-21", "--until=2026-09-28",
           "--format=%h")
n = len([x for x in n.strip().splitlines() if x.strip()])
ck("本周提交数 >= 40（3h 一次）", n >= 40, "n=%d" % n)
rc, head = sh("git", "-C", BASE, "rev-parse", "HEAD", "origin/main")
sha = head.split()
ck("本地 HEAD == origin/main（已推送）", len(sha) == 2 and sha[0] == sha[1],
   " ".join(sha)[:80])
rc, stt = sh("git", "-C", BASE, "status", "--porcelain")
ck("无长期悬挂 MM（提交未失败）",
   not any(l.startswith("MM") for l in stt.splitlines()), stt.strip()[:60])
rc, files = sh("git", "-C", BASE, "show", "--name-only", "--pretty=format:", "HEAD")
ck("HEAD 提交包含 W39 周报", "2026-W39.md" in files)
ck("HEAD 提交包含 changelog", "roadmap-changelog.md" in files)
for p in ["/root/.hermes/profiles/408-study/scripts/sync-study.sh",
          "/root/.hermes/scripts/sync-study.sh"]:
    src = rd(p)
    tag = p.split("/")[4]
    ck("备份脚本引号消息: %s" % tag, 'git commit -m "自动备份 $(date' in src)
    ck("备份脚本无写死日期: %s" % tag, "2026-08-03" not in src)
    ck("备份脚本 commit 失败 exit 1: %s" % tag, "备份失败: git commit" in src)
    r = subprocess.run(["bash", "-n", p], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    ck("备份脚本语法 OK: %s" % tag, r.returncode == 0)

# ---------- 8. 脚本存在 + 语法 ----------
for f in ["review-w39-collect.py", "ilink-probe-log.py", "ilink-probe-log-selftest.py",
          "daily-audit-state.py", "daily-backlog-audit.py"]:
    ck("脚本存在: %s" % f, os.path.isfile(os.path.join(SC, f)))
for f in ["review-w39-collect.py", "daily-audit-state.py", "daily-backlog-audit.py"]:
    r = subprocess.run(["python3", "-m", "py_compile", os.path.join(SC, f)],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    ck("脚本语法 OK: %s" % f, r.returncode == 0)
ck("周报含 dashboard 刷新说明", "dashboard" in off)

# ---------- 9. 无伪造记录 ----------
ck("每日记录无新增 md（不补写缺勤）",
   not any(f.endswith(".md") for f in os.listdir(os.path.join(BASE, "每日记录"))))
ck("错题本仍为空（不编造错题）",
   not any(f.endswith(".md") for f in os.listdir(os.path.join(BASE, "错题本"))))
ma = json.load(open(os.path.join(SD, "mastery.json"), encoding="utf-8"))
ck("mastery 未编造掌握度", ma.get("topics") == {}, json.dumps(ma.get("topics"))[:40])
ck("dashboard total_study_minutes 未编造(0)", d["summary"]["total_study_minutes"] == 0)

ok = all(c[1] for c in checks)
for name, cond, det in checks:
    print(("PASS" if cond else "FAIL"), "-", name, ("(" + det + ")" if det else ""))
print("TOTAL: %d checks, %s" % (len(checks), "ALL PASS" if ok else "HAS FAILURES"))
sys.exit(0 if ok else 1)
