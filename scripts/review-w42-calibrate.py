# -*- coding: utf-8 -*-
"""W42 复盘落盘: 追加 changelog 行 + 刷新 dashboard-data.json"""
import os, subprocess

BASE = '/root/27-study'
CL = os.path.join(BASE, '状态数据/roadmap-changelog.md')

row = ("| 2026-10-18 10:05 | 周复盘（2026-W42，覆盖 10/12–10/18）：① **通道 V 型**——8/28 起第 48 天故障 → 10/15 10:46 用户入站「我还没有开始」→ 10/15 10:47 交互回复送达、21:03 晚班送达、10/16 全天正常 → **10/17 09:02 与 21:02 复发**（均 rate limited 600s→120s）→ 10/18 09:01 探测回到 `ret=-2 prepare failed`；本周 7 次发送失败、3 条到达；② **真实基线校准为 ≈0**（用户亲口「我还没有开始」，8/6「王道士第5讲」不再作为现役进度），roadmap 已排到王道第 98 讲 → 差 93 讲；③ **roadmap 零改动（有意不续排）**：tasks 205 / archived 24 / pending 181 / completed 0，末排期 9/30，`date >= 2026-10-01` = 0，phase-4 active 第 18 天零任务；④ **三个系统侧事故**：10/15 上午「清零重排」空写（已在 10/15 21:06 行记录）、10/16 与 10/17 早班把内部运维话术（verification_evidence/SKIP/断言清单）写进用户正文、10/12 与 10/14 晚班 `[SILENT]` 混写英文分析（纯静默仅 2/7）；⑤ 三条外部判据：备份链 49 次提交 + `HEAD == origin/main`、探测链 7/7 天有行、状态链 current_day 72→79 零 drift；⑥ 新假设 **H25 出站可用窗口 ≈ 入站后 24–36 小时**（最强证据：故障期所有成功发送均紧跟真人入站）、**H26 用户主动开口与提醒无关**、**H27 决策型提问回复率低于状态型提问**、H28（低压，不下结论）；⑦ `delivery_obligations` 两条 9/3 failed 继续 superseded 不补发；watchdog 8:30 假红仍未落盘（cron 内被 lifecycle_guard 拦，留给人工会话） | 判据 = `gateway.log` 逐日 send failed 行（10/16 零行、10/17 四行、10/18 两行）+ `jobs.json.last_delivery_error` + cron 归档 `## Response` 正文 + `ilink-diag.log` + `state.db` 真人入站；沿用 pitfall 19/20（job 全绿 ≠ 送达、退出码 0 ≠ 做成）与「reset 需用户确认、不擅自续排」 |\n")

existing = open(CL, encoding='utf-8').read()
if '| 2026-10-18 10:05 |' in existing:
    print('changelog 已有 W42 行 → 跳过追加（幂等）')
else:
    with open(CL, 'a', encoding='utf-8') as f:
        f.write(row)
    print('changelog appended, new size =', os.path.getsize(CL))

r = subprocess.run(['python3', '/root/.hermes/profiles/408-study/scripts/dashboard-refresh.py'],
                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
print('dashboard refresh rc =', r.returncode)
print(r.stdout.decode('utf-8', 'replace')[-800:])

# 口径守卫：陈旧脚本 review-dashboard-refresh.py（写死 today='2026-08-09'）会把 overdue 写成 30
import json
db = json.load(open(os.path.join(BASE, '状态数据/dashboard-data.json'), encoding='utf-8'))
if db['tasks']['overdue_tasks'] != 181 or db['progress']['current_day'] != 79:
    raise SystemExit('FAIL dashboard 口径: overdue=%s current_day=%s'
                     % (db['tasks']['overdue_tasks'], db['progress']['current_day']))
print('dashboard 口径 OK: overdue=181 current_day=79')
