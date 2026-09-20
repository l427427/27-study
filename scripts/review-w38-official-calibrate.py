# -*- coding: utf-8 -*-
"""W38 正式版复盘 · 数据校准（原子写入）。
1) system-state.json: today_session.date → 2026-09-20, current_day → 51, status → day_closed
2) roadmap-changelog.md: 追加 W38 正式版一行
只改这两处；roadmap.json 内容/weekly 报告不动。
"""
import json
import os
import shutil

BASE = '/root/27-study'
SS = os.path.join(BASE, '状态数据/system-state.json')
CL = os.path.join(BASE, '状态数据/roadmap-changelog.md')

# ---------- 1. system-state ----------
st = json.load(open(SS, encoding='utf-8'))
before = (st['current_project']['current_day'], st['today_session']['date'])
st['current_status'] = 'day_closed'
st['current_project']['current_day'] = 51          # 7/31 = day0 → 9/20 = day51
st['today_session']['date'] = '2026-09-20'
st['today_session']['status'] = 'day_closed'
st['today_session']['actual_minutes_available'] = 390
st['today_session']['current_stage'] = 'review_maintenance'
st['updated_at'] = '2026-09-20T10:05:00'

tmp = SS + '.tmp'
with open(tmp, 'w', encoding='utf-8') as f:
    json.dump(st, f, ensure_ascii=False, indent=2)
    f.write('\n')
os.replace(tmp, SS)
print('system-state: day %s→%s, date %s→%s, status=%s' % (
    before[0], st['current_project']['current_day'], before[1],
    st['today_session']['date'], st['current_status']))

after = json.load(open(SS, encoding='utf-8'))
assert after['current_project']['current_day'] == 51
assert after['today_session']['date'] == '2026-09-20'
print('  verify: 重读 OK (day=%s, date=%s)' % (
    after['current_project']['current_day'], after['today_session']['date']))

# ---------- 2. changelog ----------
shutil.copy2(CL, CL + '.bak-w38')
row = (
    "| 2026-09-20 10:05 | 周复盘（2026-W38 **正式版**，覆盖 9/14–9/20；9/17 补跑版留档 "
    "`2026-W38-补跑版-20260917.md`）：① **备份链静默故障定位+修复**——`sync-study.sh` 提交消息未加引号，"
    "git 把日期当 pathspec 直接 `fatal: pathspec '2026-08-03' did not match`，再被 `>/dev/null 2>&1` 吞掉，"
    "job 连续 3 天报 `ok` 却零提交（9/17 12:23 后无新提交；`--dry-run` 已复现）；改为消息整体加引号 + "
    "`$(date '+%Y-%m-%d %H:%M')` 动态日期 + commit 失败 `exit 1`，profile/global 两处副本同步，"
    "并把「GitHub 最新提交时间」列为周报固定检查项；② **探测链断点修复**——9/18、9/19 无探测行"
    "（其余 5 天有），根因 = 每日 09:00 job 未挂运维手册、prompt 无探测步骤，「每日固定动作」靠 LLM 自觉"
    "→ 已 `hermes cron edit 0d34337730f8 --add-skill ai-mentor-review-ops`，并新增一键包装器 "
    "`ilink-probe-log.py`（探测 + 自动落 `ilink-diag.log`，LLM 不再编辑文件；stub harness 12 项断言全 PASS）；"
    "③ 通道第 24 天复测：`ret=-2 prepare failed`（HTTP200 / 804ms），签名不变，本端不可修，等用户侧重登；"
    "④ roadmap 内容**无调整**（第 5 周，phase-3 t113–t205 保守基线；phase-3 仅剩 10 天至 9/30 收口，"
    "phase-4 节奏需用户拍板，写成问句、不自作主张）；⑤ system-state 9/17 → 9/20（第 48 → **51** 天）；"
    "⑥ dashboard 复核：overdue 148（排除 24 项归档）与 roadmap 独立重数一致、completed=0 未伪造；"
    "⑦ 用户「从头开始任务吧」（9/3）第 4 周悬置，**未擅动 roadmap 结构**；⑧ 用户侧 17 天零入站、"
    "`delivery_obligations` 2 条 failed（9/3 的两条回复）`attempts=0` 从未重试，恢复后第一优先补发；"
    "⑨ 新假设 H19（「退出码 0」≠ 做成了：备份 0 提交 + 提醒 0 送达，本周两处实证）/ H20"
    "（靠 LLM 自觉的固定动作在无人监督时必漏），两条均已当场整改 | 本周两次「job 全绿但事情没做成」，"
    "共同教训 = 只看退出码会误判；已按「让失败变红 + 加外部判据（探测行 / GitHub 提交时间）」整改 |\n")

with open(CL, 'a', encoding='utf-8') as f:
    f.write(row)
txt = open(CL, encoding='utf-8').read()
assert '2026-09-20 10:05' in txt
print('changelog: 已追加 W38 正式版行 (bytes=%d)' % len(txt))
