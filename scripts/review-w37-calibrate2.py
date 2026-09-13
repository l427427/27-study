#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-W37 周复盘校准（服务器执行版，2026-09-13 周日 cron）。

动作：
 1. system-state.json 推进：9/6 → 9/13，current_day 38 → 44（含 W36 off-by-one 修正）
 2. roadmap.json metadata.last_review 更新
 3. roadmap-changelog.md 追加 2026-09-13 行
 4. .env 放宽本地熔断（600s/1 → 120s/2），下次 gateway 重启生效（先备份 .env.bak-w37）
所有 JSON 写入先写 .tmp 再 os.replace（原子）。
注意：本脚本不修改 roadmap 任务内容（phase-3 保守基线不动），不标记任何 completed。
"""
import json
import os
import tempfile

BASE = '/root/27-study/状态数据'
ENV = '/root/.hermes/profiles/408-study/.env'


def atomic_write_json(path, obj, single_line=False):
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, suffix='.tmp')
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        if single_line:
            json.dump(obj, f, ensure_ascii=False)
        else:
            json.dump(obj, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)
    print('written:', path)


# ---- 1. system-state.json ----
p = os.path.join(BASE, 'system-state.json')
ss = json.load(open(p, encoding='utf-8'))
ss['current_project']['current_day'] = 44          # 2026-09-13 - 2026-07-31 = 44 天
ss['today_session']['date'] = '2026-09-13'
ss['today_session']['status'] = 'day_closed'
ss['today_session']['started_at'] = '2026-09-13T09:00:00'
ss['today_session']['current_stage'] = 'opening'
ss['today_session']['completed_topics'] = []
ss['last_session'] = {
    'date': '2026-09-03',
    'status': 'no_report',
    'ended_at_stage': 'user_initiated',
    'last_topic': '用户主动消息：最近都没有继续完成任务 / 从头开始任务吧（2 条回复投递失败，至今未送达）',
}
ss['updated_at'] = '2026-09-13T10:20:00'
atomic_write_json(p, ss)

# ---- 2. roadmap.json metadata.last_review ----
p = os.path.join(BASE, 'roadmap.json')
rm = json.load(open(p, encoding='utf-8'))
rm['metadata']['last_review'] = (
    '2026-09-13: 2026-W37 周复盘（周日 cron）。用户自 9/3 后零新消息（入站静默 10 天）；'
    '出站连续 16 天 0 送达：降频 18 倍（18→1 次/天）连 7 天仍零恢复，H10「高频触发限流」'
    '基本否定，故障改判为平台侧发送前置校验失败（sendmessage → ret=-2/errmsg=prepare failed，'
    'HTTP 200；getconfig ret=0 → token 有效）。新发现：本地熔断（threshold=1/open=600s）'
    '使 9/3 的两条回复在本地就被挡掉、从未真正发往 iLink → 入站触发的回复是否可用仍未验证'
    '（H15）。已放宽熔断至 120s/2 次（.env，重启生效）。roadmap 无内容调整（phase-3 保守基线）。'
)
atomic_write_json(p, rm, single_line=True)

# ---- 3. changelog ----
cl_path = os.path.join(BASE, 'roadmap-changelog.md')
row = (
    '| 2026-09-13 | 周复盘（2026-W37）：① **H10 基本否定**——止血生效（executions.db 证明'
    '1e4a4ce7438c/5f3a2b1c9d8e 自 9/6 09:30 起 0 次执行），投递尝试量从 18 次/天降到 1 次/天'
    '（gateway.log 8/28–9/5 每天 ~36 行 → 9/7 起 4 行/天），**连 7 天仍 0 恢复** →「高频触发限流、'
    '降频即解」不成立；② **故障定性再升级**：9/13 复测 `sendmessage` 仍 `{"ret":-2,"errmsg":"prepare failed"}`'
    '（HTTP 200 / 743ms），`getconfig ret=0`（token 有效），且 `getupdates` 出现 15s 超时 → 平台侧'
    '发送前置校验失败，本端不可修，需用户侧重登 iLink bot；③ **新发现：本地熔断吞掉 9/3 的回复**'
    '（.env WEIXIN_RATE_LIMIT_CIRCUIT_OPEN_SECONDS=600 + threshold=1 → 当日 10:30:27 逐项提醒失败后'
    '开 600s 熔断，10:31 的两条回复记 cooldown 521s/564s，**从未真正发往 iLink**）→ 提出 H15'
    '「入站触发的回复仍可能可行」，为下周最高价值实验；已放宽熔断为 120s/2 次（先备份 .env.bak-w37，'
    '下次 gateway 重启生效，**本次不重启**以保住唯一在线入站通道）；④ roadmap 无内容调整'
    '（phase-3 t113–t205 保守基线第 3 周不动，无任何用户实报）；⑤ system-state 9/6 → 9/13，'
    'current_day 38 → **44**（并按既有口径 day=距 7/31 天数 修正 W36 的 off-by-one：9/6 应为 37）；'
    '⑥ 用户「从头开始任务吧」（9/3）连续第 2 周悬置，**未擅自重置 roadmap**，列为渠道恢复后 P1 | '
    '本周把「限流」彻底改判为「平台侧前置校验失败」，并首次发现「本地熔断会让回复根本没发出去」'
    '这一自伤机制——后者是 16 天来第一条指向「还能救」的证据 |\n'
)
with open(cl_path, encoding='utf-8') as f:
    cl = f.read()
if any(line.startswith('| 2026-09-13') for line in cl.splitlines()):
    print('changelog already has 2026-09-13 row, skip')
else:
    with open(cl_path, 'a', encoding='utf-8') as f:
        f.write(row)
    print('changelog appended')

# ---- 4. .env 熔断放宽（备份优先，幂等） ----
with open(ENV, encoding='utf-8') as f:
    env_lines = f.read().splitlines()
bak = ENV + '.bak-w37'
if not os.path.exists(bak):
    with open(bak, 'w', encoding='utf-8') as f:
        f.write('\n'.join(env_lines) + '\n')
    print('backup written:', bak)

out, seen = [], set()
for line in env_lines:
    if line.startswith('WEIXIN_RATE_LIMIT_CIRCUIT_OPEN_SECONDS'):
        out.append('WEIXIN_RATE_LIMIT_CIRCUIT_OPEN_SECONDS=120')
        seen.add('open')
    elif line.startswith('WEIXIN_RATE_LIMIT_CIRCUIT_THRESHOLD'):
        out.append('WEIXIN_RATE_LIMIT_CIRCUIT_THRESHOLD=2')
        seen.add('thr')
    else:
        out.append(line)
if 'open' not in seen:
    out.append('WEIXIN_RATE_LIMIT_CIRCUIT_OPEN_SECONDS=120')
if 'thr' not in seen:
    out.append('WEIXIN_RATE_LIMIT_CIRCUIT_THRESHOLD=2')
fd, tmp = tempfile.mkstemp(dir=os.path.dirname(ENV), suffix='.tmp')
with os.fdopen(fd, 'w', encoding='utf-8') as f:
    f.write('\n'.join(out) + '\n')
os.chmod(tmp, 0o600)
os.replace(tmp, ENV)
print('env updated (open=120, threshold=2)')

print('done.')
