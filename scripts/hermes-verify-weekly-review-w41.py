#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""W41 周复盘 · 落盘校验（ad-hoc，非正式测试套件）。
用法: python3 hermes-verify-weekly-review-w41.py
覆盖：周报落盘 / changelog（含两条整改记录）/ system-state 零 drift / dashboard /
      roadmap 独立重数 + 排期耗尽(10/1 起 0 任务) / phase 状态 / 探测 7/7 /
      备份链 git 判据 / 408 编号链分段 / 本周整改（jobs.json 补挂手册）/
      watchdog 未落盘（lifecycle_guard 拦截）/ 无伪造记录
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
checks = []


def ck(name, cond, detail=""):
    checks.append((name, bool(cond), detail))


def rd(p):
    return open(p, encoding="utf-8").read()


def sh(*args):
    r = subprocess.run(list(args), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return r.returncode, r.stdout.decode("utf-8", "replace")


# ---------- 1. 周报落盘 ----------
p_off = os.path.join(WEEK, "2026-W41.md")
ck("W41 周报存在", os.path.isfile(p_off),
   "%d bytes" % (os.path.getsize(p_off) if os.path.isfile(p_off) else 0))
off = rd(p_off) if os.path.isfile(p_off) else ""
ck("标题含 W41", "2026-W41 周复盘" in off)
ck("覆盖 10/5–10/11", "10/5–10/11" in off)
ck("含 8 个章节", off.count("\n## ") >= 8, "## 数=%d" % off.count("\n## "))
for kw in ["计划 vs 实际完成", "学习模式识别", "下周建议", "高频错题",
           "用户本周对自己的一个新认识", "Roadmap 与系统侧调整"]:
    ck("含小节关键词: %s" % kw, kw in off)
ck("写明排期耗尽 + 10/1 起 0 排期", "排期耗尽" in off and "2026-10-01" in off)
ck("写明 11 个 0 任务日（第 2 周）", "11 个 0 任务日" in off)
ck("写明 phase-4 active / phase-3 closed", "phase-4" in off and "closed" in off)
ck("写明通道第 44 天", "第 44 天" in off)
ck("写明用户 38 天零入站", "38" in off and "零入站" in off)
ck("含新假设 H23", "H23" in off)
ck("含新假设 H24", "H24" in off)
ck("写明备份链 52 次提交", "52 次提交" in off)
ck("写明探测链 7/7", "7/7" in off and "ilink-diag.log" in off)
ck("写明状态链零 drift", "drift" in off)
ck("写明未伪造完成数", "completed=0" in off or "completed = 0" in off)
ck("写明 21:00 班 10/10 违规（花式重复）", "花式重复" in off)
ck("写明 watchdog 假红（68 次补发失败）", "68 次" in off)
ck("写明 lifecycle_guard 拦截原因", "embedded null byte" in off or "lifecycle_guard" in off)
ck("写明本轮唯一落盘改动 = 补挂手册", "补挂" in off and "ai-mentor-review-ops" in off)
ck("未编造用户自我认识", "不编造" in off)

# ---------- 2. changelog ----------
cl = rd(os.path.join(SD, "roadmap-changelog.md"))
ck("changelog 含 W41 行", "2026-10-11 10:05" in cl and "2026-W41" in cl)
ck("changelog 记录补挂手册整改", "2026-10-11 10:03" in cl and "--add-skill ai-mentor-review-ops" in cl)
ck("changelog 记录 watchdog 未落盘", "2026-10-11 10:04" in cl and "未落盘" in cl)
ck("changelog 保留 10/1 排期耗尽行", "2026-10-01 09:00" in cl and "排期耗尽" in cl)
ck("changelog 保留 W40 行", "2026-10-04 10:05" in cl and "2026-W40" in cl)

# ---------- 3. system-state（零 drift）----------
st = json.load(open(os.path.join(SD, "system-state.json"), encoding="utf-8"))
ck("current_day == 72（嵌套路径）", st["current_project"]["current_day"] == 72,
   str(st["current_project"]["current_day"]))
ck("today_session.date == 2026-10-11",
   st["today_session"]["date"] == "2026-10-11", st["today_session"]["date"])
ck("current_status == day_closed", st["current_status"] == "day_closed",
   st["current_status"])
ck("last_session 未伪造(仍 no_report)",
   st["last_session"]["status"] == "no_report", st["last_session"]["status"])
ck("updated_at 是今天（零 drift）",
   str(st.get("updated_at", "")).startswith("2026-10-11"), st.get("updated_at"))

# ---------- 4. dashboard ----------
d = json.load(open(os.path.join(SD, "dashboard-data.json"), encoding="utf-8"))
ck("dashboard current_day == 72", d["progress"]["current_day"] == 72)
ck("dashboard days_remaining == 76", d["progress"]["days_remaining"] == 76)
ck("dashboard overdue == 181", d["tasks"]["overdue_tasks"] == 181,
   str(d["tasks"]["overdue_tasks"]))
ck("dashboard completed == 0（未伪造）", d["tasks"]["completed_tasks"] == 0)
ck("dashboard total == 205", d["tasks"]["total_tasks"] == 205)
ck("dashboard 科目总和 == 205",
   sum(v["total_tasks"] for v in d["subjects"].values()) == 205)
ck("dashboard phase-3 closed", d["phases"]["phase-3"]["status"] == "closed",
   d["phases"]["phase-3"]["status"])
ck("dashboard phase-4 active", d["phases"]["phase-4"]["status"] == "active",
   d["phases"]["phase-4"]["status"])

# ---------- 5. roadmap 独立重数 + phase + 排期耗尽 ----------
rm = json.load(open(os.path.join(SD, "roadmap.json"), encoding="utf-8"))
ts = rm["tasks"]
ck("roadmap 任务总数 == 205", len(ts) == 205, str(len(ts)))
ck("roadmap completed == 0（未伪造）",
   sum(1 for t in ts if t.get("status") == "completed") == 0)
od = [t for t in ts if t.get("date", "") < "2026-10-11"
      and t.get("status") != "completed" and not t.get("archived")]
ck("逾期重数 == 181（排除 archived）", len(od) == 181, str(len(od)))
ck("归档 == 24", sum(1 for t in ts if t.get("archived")) == 24)
ph = {p["id"]: p["status"] for p in rm["phases"]}
ck("roadmap phase-3 == closed", ph.get("phase-3") == "closed", str(ph))
ck("roadmap phase-4 == active", ph.get("phase-4") == "active", str(ph))
ck("phase-5 仍 upcoming", ph.get("phase-5") == "upcoming", str(ph))
ck("本周未改任务（tasks 仍全 pending）",
   all(t.get("status") == "pending" for t in ts))
ck("roadmap 内容零改动（tasks 数未变）", len(ts) == 205 and len(od) == 181)
win = [t for t in ts if "2026-10-05" <= t.get("date", "") <= "2026-10-11"]
ck("W41 窗口任务 == 0 项（排期耗尽）", len(win) == 0, str(len(win)))
ck("排期耗尽：date >= 2026-10-01 任务数 == 0",
   sum(1 for t in ts if t.get("date", "") >= "2026-10-01") == 0)
ck("roadmap 末排期 == 2026-09-30", max(t["date"] for t in ts) == "2026-09-30")
ck("roadmap 最早未完成 == t025(8/4)",
   min(t["date"] for t in od) == "2026-08-04" and
   any(t["id"] == "t025" for t in od))
# 408 编号链：先按「有意重启」分段，再断言每段内部连续（W38 口径）
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

# ---------- 6. 探测日志（W41：10/5–10/11 应 7/7 天有行）----------
dl = rd(os.path.join(SC, "ilink-diag.log"))
wk_days = ["2026-10-%02d" % dd for dd in range(5, 12)]
have = [x for x in wk_days if ("%s " % x) in dl]
ck("ilink-diag.log 本周 7/7 天有探测行", len(have) == 7, str(have))
ck("10/11 探测行已记录", "2026-10-11 09:00" in dl)
ck("本周探测均记为未恢复/签名不变",
   all("未恢复" in ln or "prepare failed" in ln
       for ln in dl.splitlines() if ln.startswith(tuple(wk_days))))

# ---------- 7. 备份链整周验证（H19 外部判据）----------
rc, n = sh("git", "-C", BASE, "log", "--since=2026-10-05", "--until=2026-10-12",
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
ck("HEAD 提交包含 W41 周报", "2026-W41.md" in files, files.strip()[:100])
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

# ---------- 8. 本周整改：jobs.json 补挂手册（H23）----------
jp = os.path.join(PROF, "cron/jobs.json")
jd = json.load(open(jp, encoding="utf-8"))
jobs = jd["jobs"] if isinstance(jd, dict) else jd
jmap = {j.get("id"): j for j in jobs}
ck("jobs.json 备份存在（.bak-w41）",
   os.path.isfile(os.path.join(PROF, "cron/jobs.json.bak-w41")))
for jid, want_sched, want_deliver in [
        ("55bd60a924fd", "0 21 * * *",
         "weixin:o9cq80xXfVrX59q6bhF9e2F8qk68@im.wechat"),
        ("660d273a3024", "0 10 * * 0",
         "weixin:o9cq80xXfVrX59q6bhF9e2F8qk68@im.wechat")]:
    j = jmap.get(jid) or {}
    ck("job %s 已挂 ai-mentor-review-ops" % jid,
       "ai-mentor-review-ops" in (j.get("skills") or []), str(j.get("skills")))
    ck("job %s 仍挂主 skill" % jid,
       "ai-learning-mentor" in (j.get("skills") or []))
    ck("job %s 排期未变" % jid,
       (j.get("schedule") or {}).get("display") == want_sched,
       str((j.get("schedule") or {}).get("display")))
    ck("job %s 投递目标未变" % jid, j.get("deliver") == want_deliver,
       str(j.get("deliver")))
    ck("job %s 仍启用/未暂停" % jid,
       j.get("state") == "scheduled" and j.get("enabled") is True,
       "%s/%s" % (j.get("state"), j.get("enabled")))
ck("09:00 job 未被误动（仍挂两手册）",
   set(jmap.get("0d34337730f8", {}).get("skills") or []) ==
   {"ai-learning-mentor", "ai-mentor-review-ops"})
ck("已暂停 job 未被误恢复（1e4a/5f3a 仍 paused）",
   (jmap.get("1e4a4ce7438c") or {}).get("state") == "paused" and
   (jmap.get("5f3a2b1c9d8e") or {}).get("state") == "paused",
   "%s/%s" % ((jmap.get("1e4a4ce7438c") or {}).get("state"),
              (jmap.get("5f3a2b1c9d8e") or {}).get("state")))

# ---------- 9. watchdog 未落盘（lifecycle_guard 拦截，H24）----------
WD = "/root/verify-morning-reminders.sh"
ck("watchdog 脚本存在", os.path.isfile(WD))
import datetime as _dt
ck("watchdog mtime 仍是 8 月（未落盘）",
   _dt.datetime.fromtimestamp(os.path.getmtime(WD)).strftime("%Y-%m") == "2026-08",
   _dt.datetime.fromtimestamp(os.path.getmtime(WD)).strftime("%Y-%m-%d %H:%M"))
ck("未留下 watchdog 备份文件（补丁未执行）",
   not any(f.startswith("verify-morning-reminders") and ".bak" in f
           for f in os.listdir("/root")))

# ---------- 10. 脚本存在 + 语法 ----------
for f in ["hermes-verify-weekly-review-w41.py", "review-w40-collect.py",
          "review-w40-calibrate.py", "ilink-probe-log.py",
          "ilink-probe-log-selftest.py", "daily-audit-state.py",
          "daily-backlog-audit.py"]:
    ck("脚本存在: %s" % f, os.path.isfile(os.path.join(SC, f)))
for f in ["hermes-verify-weekly-review-w41.py", "daily-audit-state.py",
          "daily-backlog-audit.py"]:
    r = subprocess.run(["python3", "-m", "py_compile", os.path.join(SC, f)],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    ck("脚本语法 OK: %s" % f, r.returncode == 0)
ck("无重复即席脚本残留（pitfall 22）",
   not os.path.exists(os.path.join(SC, "check-oct1-reminder.py")))
ck("周报含 dashboard 刷新说明", "dashboard" in off)

# ---------- 11. 无伪造记录 ----------
ck("每日记录无新增 md（不补写缺勤）",
   not any(f.endswith(".md") for f in os.listdir(os.path.join(BASE, "每日记录"))))
ck("错题本仍为空（不编造错题）",
   not any(f.endswith(".md") for f in os.listdir(os.path.join(BASE, "错题本"))))
ma = json.load(open(os.path.join(SD, "mastery.json"), encoding="utf-8"))
ck("mastery 未编造掌握度", ma.get("topics") == {}, json.dumps(ma.get("topics"))[:40])
ck("dashboard total_study_minutes 未编造(0)", d["summary"]["total_study_minutes"] == 0)
ck("roadmap 未新增任务（未擅自续排）", len(ts) == 205)

ok = all(c[1] for c in checks)
for name, cond, det in checks:
    print(("PASS" if cond else "FAIL"), "-", name, ("(" + det + ")" if det else ""))
print("TOTAL: %d checks, %s" % (len(checks), "ALL PASS" if ok else "HAS FAILURES"))
sys.exit(0 if ok else 1)
