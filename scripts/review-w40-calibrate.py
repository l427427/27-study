#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""W40 校准：phase-3 到期收口（按日期事实）→ closed；phase-4 → active。
不改任何任务结构（reset 待用户确认）。原子写入 + 追加 changelog。"""
import json, os, datetime

BASE = '/root/27-study'
SD = os.path.join(BASE, '状态数据')
rp = os.path.join(SD, 'roadmap.json')

with open(rp, encoding='utf-8') as f:
    rm = json.load(f)

before = [(p.get('id'), p.get('status')) for p in rm['phases']]
for p in rm['phases']:
    if p.get('id') == 'phase-3':
        p['status'] = 'closed'
    elif p.get('id') == 'phase-4':
        p['status'] = 'active'
after = [(p.get('id'), p.get('status')) for p in rm['phases']]

# 原子写：tmp -> os.replace，保持单行
tmp = rp + '.tmp'
with open(tmp, 'w', encoding='utf-8') as f:
    json.dump(rm, f, ensure_ascii=False)
os.replace(tmp, rp)

print("phase status:", before, "->", after)
ntasks = len(rm['tasks'])
print("tasks unchanged:", ntasks, "| tasks_total:", len(rm['tasks']))
print("no task touched:", all('date' in t for t in rm['tasks']))

# 复核落盘
with open(rp, encoding='utf-8') as f:
    chk = json.load(f)
print("reload phases:", [(p.get('id'), p.get('status')) for p in chk['phases']])
print("reload tasks:", len(chk['tasks']))

# changelog 追加
cl = os.path.join(SD, 'roadmap-changelog.md')
row = (
    "| 2026-10-04 10:05 | 周复盘（2026-W40，覆盖 9/28–10/4）：① **排期耗尽成硬事实**——roadmap 未归档任务日期跨度 2026-08-04 → **2026-09-30**，"
    "`2026-10-01` 起 0 排期（roadmap 中 `date >= 2026-10-01` 的任务数 = 0），本周 10/1–10/4 连续 4 天「今日 0 项」；"
    "**未自动续排**（用户 9/3「从头开始任务吧」reset 请求未确认，优先级高于续排），沿用 10/1 决定；"
    "② **phase 状态按日期事实校准**：phase-3（8/28–9/30）→ `closed`，phase-4（10/1–11/30「全科深度推进」）→ `active`"
    "（仅改 phase.status，**未动任何任务**，tasks 仍 205 项全 pending；若用户确认 reset 可随重排一并作废）；"
    "③ W39 两条整改**通过整周外部判据**（第 2 周）：备份链 9/28–10/4 共 48 次提交、`HEAD == origin/main`、无悬挂 `MM`；"
    "探测链 `ilink-diag.log` 9/28–10/4 **7/7 天每天 1 行**；④ **W39「孤儿脚本」整改首次通过整周验证**："
    "`system-state.updated_at` 9/28–10/4 每天都是当天、`current_day` 59→65 逐日递增，**零 drift**；"
    "⑤ 通道第 **37** 天复测：本周 13 次投递尝试（9/28–10/3 每天 2 次 + 10/4 09:00 1 次）全失败，签名不变（本端不可修，"
    "gateway 进程 8/7 启动至今未重启，`.env` 熔断 120s/2 未生效）；⑥ 用户侧**连续第 31 天零入站**（最新真人消息仍 = 9/3 10:31），"
    "`delivery_obligations` 2 条 `failed` 仍 `attempts=0`；⑦ dashboard 复核：overdue 181（排除 24 项归档）与 roadmap 独立重数一致、"
    "completed=0 未伪造、total=205、current_day 65 / days_remaining 83；⑧ **「排期耗尽」专属配方 10/1 落地生效**：本周 4 天提醒均按配方输出"
    "（3 行状态表 + 两问句 + 通道认领），未套「计划 X 分钟」模板、未倒 181 项 backlog；⑨ 新假设 H22（排期耗尽 → 系统零可交付内容，"
    "教学闭环无法自愈）；⑩ 用户「从头开始」第 6 周悬置，未擅动 roadmap 任务结构 | "
    "本周主变量 = 计划表本身到期（首次出现「无内容可交付」），叠加通道第 37 天不通 → 教学侧连续第 11 周零闭环；"
    "系统侧连续第 2 周全绿（备份/探测/状态链三条外部判据全达标），H21（运维全绿掩盖教学零消费）本周进一步坐实 |\n"
)
with open(cl, 'a', encoding='utf-8') as f:
    f.write(row)
print("changelog appended:", os.path.getsize(cl), "bytes")
print("last line head:", open(cl, encoding='utf-8').read().strip().splitlines()[-1][:120])
