# -*- coding: utf-8 -*-
"""2026-W36 正式周复盘校准：system-state 推进 + roadmap metadata + changelog。"""
import json, os, tempfile, datetime

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
ss['current_project']['current_day'] = 38
ss['today_session']['date'] = '2026-09-06'
ss['today_session']['status'] = 'day_closed'
ss['today_session']['started_at'] = '2026-09-06T09:00:00'
ss['updated_at'] = '2026-09-06T10:20:00'
atomic_write_json(p, ss)

# ---- 2. roadmap.json metadata.last_review ----
p = os.path.join(BASE, 'roadmap.json')
rm = json.load(open(p, encoding='utf-8'))
rm['metadata']['last_review'] = ('2026-09-06: 2026-W36 正式周复盘（周日 cron）。'
                                 '用户 9/3 主动消息（最近没完成任务/从头开始任务吧）2 条收到但回复全部投递失败；'
                                 'P0 iLink 投递故障 9/2-9/6 持续；已暂停本机高频微信投递 job 止血；'
                                 'roadmap 无内容调整（phase-3 保守基线等待用户实报）。')
atomic_write_json(p, rm)

# ---- 3. changelog append ----
cl_path = os.path.join(BASE, 'roadmap-changelog.md')
with open(cl_path, encoding='utf-8') as f:
    cl = f.read()
row = (
    '| 2026-09-06 | 周复盘（2026-W36 正式版，9/6 周日 10:00 cron，替代 9/1 临时版）：'
    '① **用户 9/3 10:30 主动发消息**（「最近都没有继续完成任务」「从头开始任务吧」）——入站通道正常；'
    '系统 2 条回复 + clarify 选项全部投递失败（rate limited），用户至今未收到任何回应；'
    '② P0 投递故障 9/2-9/6 持续：早 9:00/晚 21:00/每小时逐项/8:25 轮换全部 rate limited 600s（本周逐项提醒尝试 92 次、全失败），'
    '9/1 预案「停高频」此前未执行；③ **执行止血**：hermes cron pause 1e4a4ce7438c（任务逐项提醒）与 5f3a2b1c9d8e（隔天轮换提醒），'
    '保留早 9:00/晚 21:00 两条低频（渠道恢复后再评估恢复）；'
    '④ roadmap 无内容调整：phase-3（t113-t205）保守基线不动，等待用户实报 408 进度后全链前移；'
    '⑤ system-state 9/1 → 9/6（第 38 天）；'
    '⑥ 用户「从头开始任务吧」= reset 请求但范围未确认（1/2/3 选项未送达），'
    '列为渠道恢复后第一优先确认项，**未擅动 roadmap 结构** | '
    '9/1 定位 P0 后一周无缓解迹象（冷却持续 600s、0 送达），且 9/3 用户主动联系被系统静默吞掉——'
    '必须停止高频请求加剧限流，并把用户真实意图记为最高优先级待办 |'
)
if '2026-09-06' not in cl:
    with open(cl_path, 'a', encoding='utf-8') as f:
        f.write('\n' + row + '\n')
    print('changelog appended')
else:
    print('changelog already has 2026-09-06 row, skip')

print('done.')
