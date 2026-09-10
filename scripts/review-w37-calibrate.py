#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-W37 周复盘校准：system-state 推进 + roadmap metadata + changelog 追加。

关键结论（W37, 9/7-9/10）：
- 用户自 9/3 后无任何新消息（入站静默 7 天）
- 出站仍 100% 失败，但异常签名升级：受控探测拿到 ret=-2/errmsg="prepare failed"
  且 token 有效（非 -14 会话过期、非鉴权错误）→ 平台侧发送前置校验失败
- 高频止血已生效（1e4a4ce7438c / 5f3a2b1c9d8e 暂停），但这几天的失败集中在
  早 9:00 / 晚 21:00 两条低频 + http 探测 → 降频未使通道自愈（H10 不成立/不足）
- 本机 MAC 侧 ticker 仍在尝试投递（12:08 撞 30s 冷却）→ 双机同账号仍需收敛
"""
import json, os, tempfile

BASE = '/root/27-study/状态数据'


def atomic_write_json(path, obj):
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, suffix='.tmp')
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False)
    os.replace(tmp, path)
    print('written:', path)


# ---- 1. system-state.json ----
p = os.path.join(BASE, 'system-state.json')
ss = json.load(open(p, encoding='utf-8'))
ss['current_project']['current_day'] = 42
ss['today_session']['date'] = '2026-09-10'
ss['today_session']['status'] = 'day_closed'
ss['today_session']['started_at'] = '2026-09-10T09:00:00'
ss['today_session']['completed_topics'] = []
ss['last_session'] = {
    'date': '2026-09-03',
    'status': 'no_report',
    'ended_at_stage': 'user_initiated',
    'last_topic': '用户主动消息：最近都没有继续完成任务 / 从头开始任务吧（回复投递失败，未送达）',
}
ss['updated_at'] = '2026-09-10T12:20:00'
atomic_write_json(p, ss)

# ---- 2. roadmap.json metadata.last_review ----
p = os.path.join(BASE, 'roadmap.json')
rm = json.load(open(p, encoding='utf-8'))
rm['metadata']['last_review'] = (
    '2026-09-10: 2026-W37 周复盘（周四 cron，因本周日 9/13 复盘窗口外提前）。'
    '用户自 9/3 后零消息（入站静默 7 天）；出站 100% 失败且签名升级为 '
    'ret=-2/errmsg=prepare failed（受控探测证实 token 有效，平台侧发送前置校验失败，'
    '非会话过期/非鉴权错误）；降频止血后通道未自愈（H10 不足）；'
    'roadmap 无内容调整（phase-3 保守基线，等待用户实报）。'
)
atomic_write_json(p, rm)

# ---- 3. roadmap-changelog.md append ----
cl_path = os.path.join(BASE, 'roadmap-changelog.md')
with open(cl_path, encoding='utf-8') as f:
    cl = f.read()
row = (
    '| 2026-09-10 | 周复盘（2026-W37）：① **P0 故障定性升级**——受控探测'
    '（独立通道直调 ilink/bot/sendmessage）拿到原始响应 `{"ret":-2,"errmsg":"prepare failed"}`，'
    'HTTP 200、耗时 825ms → **token 有效（非 -14 会话过期、非鉴权失败），失败发生在平台侧发送前置校验**；'
    'weixin.py 将其归类为 RATE_LIMIT_ERRCODE=-2，故全部日志显示「rate limited」，'
    '**此前「平台限流」的诊断需要修正为「发送前置校验失败」**；'
    '② 降频止血（9/6 暂停 1e4a4ce7438c/5f3a2b1c9d8e）已生效但**通道未自愈**：'
    '9/7-9/10 失败集中在早 9:00/晚 21:00 两条低频（每日 1-2 次 delivery error）+ 报警通道探测，'
    'H10「高频触发限流→降频即解」**证据不足，暂不成立**；'
    '③ **发现本机 MAC 侧 ticker 仍在尝试投递**（9/10 12:08 撞 30s 冷却，jobs.json 本机副本 7 个 job 全部 enabled，'
    '与服务器侧 paused 状态不一致）→ 双机同 iLink 账号（md5 校验一致）仍在重复尝试，需收敛；'
    '④ roadmap 无内容调整：phase-3（t113-t205）保守基线不动；'
    '⑤ system-state 9/6 → 9/10（第 38 → 42 天）；'
    '⑥ 用户「从头开始任务吧」（9/3）仍为渠道恢复后第一优先确认项，**连续第 2 周未擅动 roadmap 结构** | '
    '本周首次用独立探测拿到了原始 API 响应，把「限流」从假设推进为可证伪的定性结论；'
    '同时暴露降频不足以恢复、以及本机副本未同步暂停两个新问题 |'
)
if not any(line.startswith('| 2026-09-10') for line in cl.splitlines()):
    with open(cl_path, 'a', encoding='utf-8') as f:
        f.write('\n' + row + '\n')
    print('changelog appended')
else:
    print('changelog already has 2026-09-10 row, skip')

print('done.')
