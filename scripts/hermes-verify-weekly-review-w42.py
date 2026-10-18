#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""W42 周复盘 · 落盘校验（ad-hoc，非正式测试套件）。
用法: python3 hermes-verify-weekly-review-w42.py
覆盖：周报落盘 / changelog（W42 行 + H25 + 空写）/ system-state 零 drift /
      dashboard 口径（overdue 181，非陈旧 30）/ roadmap 独立重数 + 排期耗尽 /
      phase / 探测 7/7 / 备份链外部判据 / 408 编号链分段 /
      W42 skill 整改字符串真在文件里 / watchdog 未落盘 / 无伪造记录
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
PROF = "/root/.hermes/profiles/408-study"
SKILL = os.path.join(PROF, "skills/ai-learning/ai-mentor-review-ops/SKILL.md")
checks = []


def ck(name, cond, detail=""):
    checks.append((name, bool(cond), detail))


def rd(p):
    return open(p, encoding="utf-8").read()


def sh(*args):
    r = subprocess.run(list(args), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return r.returncode, r.stdout.decode("utf-8", "replace")


# ---------- 1. 周报落盘 ----------
p_off = os.path.join(WEEK, "2026-W42.md")
ck("W42 周报存在", os.path.isfile(p_off),
   "%d bytes" % (os.path.getsize(p_off) if os.path.isfile(p_off) else 0))
off = rd(p_off) if os.path.isfile(p_off) else ""
ck("标题含 W42", "2026-W42 周复盘" in off)
ck("覆盖 10/12–10/18", "10/12–10/18" in off)
ck("含 8 个章节以上", off.count("\n## ") >= 8, "## 数=%d" % off.count("\n## "))
for kw in ["计划 vs 实际完成", "学习模式识别", "下周", "高频错题",
           "用户本周对自己的一个新认识", "Roadmap 本周调整"]:
    ck("含小节关键词: %s" % kw, kw in off)
ck("写明第 79 天 / 剩 69 天", "第 79 天" in off and "69 天" in off)
ck("写明排期耗尽 + 18 天零任务", "排期耗尽" in off and "第 18 天" in off)
ck("写明用户亲口「我还没有开始」= 基线≈0", "我还没有开始" in off and "基线" in off)
ck("写明 7 次发送失败 / 3 条到达", "7 次发送失败" in off and "3 条" in off)
ck("写明通道断 48 天 → 通 36 小时 → 再断", "48 天" in off and "36 小时" in off)
ck("写明 10/15 空写事故", "空写" in off and "100885" in off)
ck("写明内部运维话术泄漏事故", "verification_evidence" in off and "内部" in off)
ck("写明晚间 [SILENT] 混写（纯静默 2/7）", "纯静默" in off and "2/7" in off)
ck("写明 completed=0 未伪造", "completed = 0" in off)
ck("写明错题本为空、无法分析", "无法分析" in off and "错题本" in off)
ck("写明新假设 H25/H26/H27", all(h in off for h in ("H25", "H26", "H27")))
ck("写明待验证假设、不贴固定标签", "待验证假设" in off)
ck("写明下周用单词作答（状态型提问）", "回一个字就行" in off)
ck("写明未擅自续排 roadmap", "未自动续排" in off or "不续排" in off)
ck("写明 phase-4 active 但零任务", "phase-4" in off and "零任务" in off)

# ---------- 2. changelog ----------
cl = rd(os.path.join(SD, "roadmap-changelog.md"))
ck("changelog 含 W42 行", "2026-10-18 10:05" in cl and "2026-W42" in cl)
ck("changelog 记录 H25 窗口假说", "H25" in cl)
ck("changelog 记录空写事故", "空写" in cl)
ck("changelog 记录 superseded 不补发", "superseded" in cl)
ck("changelog 保留 10/15 21:06 事故行", "2026-10-15 21:06" in cl)
ck("changelog 保留 W41 行", "2026-W41" in cl)

# ---------- 3. system-state（零 drift）----------
st = json.load(open(os.path.join(SD, "system-state.json"), encoding="utf-8"))
ck("current_day == 79（嵌套路径）", st["current_project"]["current_day"] == 79,
   str(st["current_project"]["current_day"]))
ck("today_session.date == 2026-10-18",
   st["today_session"]["date"] == "2026-10-18", st["today_session"]["date"])
ck("current_status == day_closed", st["current_status"] == "day_closed",
   st["current_status"])
ck("last_session 未伪造(仍 no_report)",
   st["last_session"]["status"] == "no_report", st["last_session"]["status"])
ck("updated_at 是今天（零 drift）",
   str(st.get("updated_at", "")).startswith("2026-10-18"), st.get("updated_at"))

# ---------- 4. dashboard 口径 ----------
d = json.load(open(os.path.join(SD, "dashboard-data.json"), encoding="utf-8"))
ck("dashboard current_day == 79", d["progress"]["current_day"] == 79)
ck("dashboard days_remaining == 69", d["progress"]["days_remaining"] == 69)
ck("dashboard overdue == 181（非陈旧脚本的 30）",
   d["tasks"]["overdue_tasks"] == 181, str(d["tasks"]["overdue_tasks"]))
ck("dashboard completed == 0（未伪造）", d["tasks"]["completed_tasks"] == 0)
ck("dashboard total == 205", d["tasks"]["total_tasks"] == 205)
ck("dashboard 科目总和 == 205",
   sum(v["total_tasks"] for v in d["subjects"].values()) == 205)
ck("dashboard 未预置政治任务(0)", d["subjects"]["政治"]["total_tasks"] == 0)
ck("dashboard phase-3 closed", d["phases"]["phase-3"]["status"] == "closed")
ck("dashboard phase-4 active", d["phases"]["phase-4"]["status"] == "active")
ck("dashboard total_study_minutes 未编造(0)", d["summary"]["total_study_minutes"] == 0)
# 刷新脚本口径：canonical 用 datetime.now()，陈旧 W32 脚本写死 today
canon = rd(os.path.join(PROF, "scripts/dashboard-refresh.py"))
ck("canonical dashboard-refresh 用动态 today",
   "datetime.now()" in canon and "strftime(\"%Y-%m-%d\")" in canon)
ck("陈旧 review-dashboard-refresh 仍写死 2026-08-09（已弃用证据）",
   "today = '2026-08-09'" in rd(os.path.join(SC, "review-dashboard-refresh.py")))

# ---------- 5. roadmap 独立重数 + phase + 排期耗尽 ----------
rm = json.load(open(os.path.join(SD, "roadmap.json"), encoding="utf-8"))
ts = rm["tasks"]
ck("roadmap 任务总数 == 205", len(ts) == 205, str(len(ts)))
ck("roadmap completed == 0（未伪造）",
   sum(1 for t in ts if t.get("status") == "completed") == 0)
od = [t for t in ts if t.get("date", "") < "2026-10-18"
      and t.get("status") != "completed" and not t.get("archived")]
ck("逾期重数 == 181（排除 archived）", len(od) == 181, str(len(od)))
ck("归档 == 24", sum(1 for t in ts if t.get("archived")) == 24)
ph = {p["id"]: p["status"] for p in rm["phases"]}
ck("roadmap phase-3 == closed", ph.get("phase-3") == "closed", str(ph))
ck("roadmap phase-4 == active", ph.get("phase-4") == "active", str(ph))
ck("phase-5 仍 upcoming", ph.get("phase-5") == "upcoming")
ck("本周未改任务（tasks 仍全 pending）",
   all(t.get("status") == "pending" for t in ts))
win = [t for t in ts if "2026-10-12" <= t.get("date", "") <= "2026-10-18"]
ck("W42 窗口任务 == 0 项（排期耗尽）", len(win) == 0, str(len(win)))
ck("排期耗尽：date >= 2026-10-01 任务数 == 0",
   sum(1 for t in ts if t.get("date", "") >= "2026-10-01") == 0)
ck("roadmap 末排期 == 2026-09-30", max(t["date"] for t in ts) == "2026-09-30")
ck("roadmap 最早未完成 == t025(8/4)",
   min(t["date"] for t in od) == "2026-08-04" and any(t["id"] == "t025" for t in od))
# 408 编号链：分段断言（W38 口径，2 处有意重启）
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

# ---------- 6. 探测日志（本周 7/7 天有行）----------
dl = rd(os.path.join(SC, "ilink-diag.log"))
wk_days = ["2026-10-%02d" % dd for dd in range(12, 19)]
have = [x for x in wk_days if ("%s " % x) in dl]
ck("ilink-diag.log 本周 7/7 天有行", len(have) == 7, str(have))
ck("10/18 探测行已落盘且为未恢复", "2026-10-18 09:01" in dl and "prepare failed" in dl)
ck("10/15 恢复行 + 裸脚本 message_id 留证",
   "2026-10-15 21:01" in dl and "7516483674502934408" in dl)

# ---------- 7. 备份链整周验证（外部判据）----------
rc, n = sh("git", "-C", BASE, "log", "--since=2026-10-12", "--until=2026-10-19",
           "--format=%h")
n = len([x for x in n.strip().splitlines() if x.strip()])
ck("本周提交数 >= 40（3h 一次）", n >= 40, "n=%d" % n)
rc, head = sh("git", "-C", BASE, "rev-parse", "HEAD", "origin/main")
sha = head.split()
ck("本地 HEAD == origin/main（已推送）", len(sha) == 2 and sha[0] == sha[1],
   " ".join(sha)[:80])
rc, stt = sh("git", "-C", BASE, "status", "--porcelain")
ck("无长期悬挂 MM（提交未失败）",
   not any(l.startswith("MM") for l in stt.splitlines()), stt.strip()[:80])
rc, files = sh("git", "-C", BASE, "show", "--name-only", "--pretty=format:", "HEAD")
ck("HEAD 提交包含 W42 周报", "2026-W42.md" in files, files.strip()[:100])
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

# ---------- 8. jobs.json（三 job 手册齐备、未被误动）----------
jp = os.path.join(PROF, "cron/jobs.json")
jd = json.load(open(jp, encoding="utf-8"))
jobs = jd["jobs"] if isinstance(jd, dict) else jd
jmap = {j.get("id"): j for j in jobs}
for jid, want_sched in [("0d34337730f8", "0 9 * * *"),
                        ("55bd60a924fd", "0 21 * * *"),
                        ("660d273a3024", "0 10 * * 0")]:
    j = jmap.get(jid) or {}
    ck("job %s skills 数组 >= 2（手册已挂）" % jid,
       len(j.get("skills") or []) >= 2 and "ai-mentor-review-ops" in (j.get("skills") or []),
       str(j.get("skills")))
    ck("job %s 排期未变" % jid,
       (j.get("schedule") or {}).get("display") == want_sched,
       str((j.get("schedule") or {}).get("display")))
    ck("job %s 仍启用/未暂停" % jid,
       j.get("state") == "scheduled" and j.get("enabled") is True,
       "%s/%s" % (j.get("state"), j.get("enabled")))
ck("已暂停 job 未被误恢复（1e4a/5f3a 仍 paused）",
   (jmap.get("1e4a4ce7438c") or {}).get("state") == "paused" and
   (jmap.get("5f3a2b1c9d8e") or {}).get("state") == "paused")

# ---------- 9. 本周 skill 整改字符串真在文件里 ----------
sk = rd(SKILL)
ck("skill 已记 review-dashboard-refresh 弃用",
   "不要用 `scripts/review-dashboard-refresh.py`" in sk)
ck("skill 已记 overdue 181 复核判据", "overdue_tasks == 181" in sk)
ck("skill 已记 H25 出站窗口假说", "出站可用窗口假说 H25" in sk)
ck("skill 已记正文禁内部运维话术", "提醒正文禁止内部运维话术" in sk)
ck("skill 原有 iLink 结论未被误删", "prepare failed" in sk and "熔断" in sk)
ck("skill 原有排期耗尽配方未被误删", "roadmap-exhaustion-handling.md" in sk)

# ---------- 10. watchdog 未落盘（lifecycle_guard 拦截）----------
WD = "/root/verify-morning-reminders.sh"
import datetime as _dt
ck("watchdog 脚本存在", os.path.isfile(WD))
ck("watchdog mtime 仍是 8 月（未落盘）",
   _dt.datetime.fromtimestamp(os.path.getmtime(WD)).strftime("%Y-%m") == "2026-08",
   _dt.datetime.fromtimestamp(os.path.getmtime(WD)).strftime("%Y-%m-%d %H:%M"))
ck("未留下 watchdog 备份文件（补丁未执行）",
   not any(f.startswith("verify-morning-reminders") and ".bak" in f
           for f in os.listdir("/root")))

# ---------- 11. 脚本存在 + 语法 ----------
for f in ["hermes-verify-weekly-review-w42.py", "review-w42-collect.py",
          "review-w42-calibrate.py", "ilink-probe-log.py", "daily-audit-state.py",
          "daily-backlog-audit.py"]:
    ck("脚本存在: %s" % f, os.path.isfile(os.path.join(SC, f)))
for f in ["hermes-verify-weekly-review-w42.py", "daily-audit-state.py",
          "daily-backlog-audit.py"]:
    r = subprocess.run(["python3", "-m", "py_compile", os.path.join(SC, f)],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    ck("脚本语法 OK: %s" % f, r.returncode == 0)
ck("无重复即席脚本残留（pitfall 22）",
   not os.path.exists(os.path.join(SC, "check-oct1-reminder.py")))

# ---------- 12. 无伪造记录 ----------
ck("每日记录无新增 md（不补写缺勤）",
   not any(f.endswith(".md") for f in os.listdir(os.path.join(BASE, "每日记录"))))
ck("错题本仍为空（不编造错题）",
   not any(f.endswith(".md") for f in os.listdir(os.path.join(BASE, "错题本"))))
ma = json.load(open(os.path.join(SD, "mastery.json"), encoding="utf-8"))
ck("mastery 未编造掌握度", ma.get("topics") == {}, json.dumps(ma.get("topics"))[:40])
ck("roadmap 未新增任务（未擅自续排）", len(ts) == 205)

ok = all(c[1] for c in checks)
for name, cond, det in checks:
    print(("PASS" if cond else "FAIL"), "-", name, (("(" + det + ")") if det else ""))
print("TOTAL: %d checks, %s" % (len(checks), "ALL PASS" if ok else "HAS FAILURES"))
sys.exit(0 if ok else 1)
