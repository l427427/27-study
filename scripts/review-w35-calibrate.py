#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-W35 周复盘数据校准（2026-08-30 执行）：
1) roadmap: phase-2 -> closed, phase-3 -> active；生成 phase-3 任务 t113-t205（8/31-9/30，每天3项）
   408 按 W34 预案最保守基线（王道第5讲）自第6讲续排，3讲/天；数学 880 180min；英语 阅读+Anki 90min
2) system-state: current_day 23->30, today_session.date -> 2026-08-30
3) roadmap-changelog.md 追加 W35 记录
所有 JSON 原子写入（tmp + os.replace）。
"""
import json, os, datetime

BASE = '/root/27-study/状态数据'
RM = os.path.join(BASE, 'roadmap.json')
SS = os.path.join(BASE, 'system-state.json')
CL = os.path.join(BASE, 'roadmap-changelog.md')

def load(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)

def atomic_dump(p, obj):
    tmp = p + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False)
    os.replace(tmp, p)

# ---------- 1. roadmap ----------
rm = load(RM)
tasks = rm['tasks']
next_id = max(int(t['id'][1:]) for t in tasks) + 1  # 113

# 1a. phase 状态切换（按日期事实，非完成度）
for p in rm['phases']:
    if p['id'] == 'phase-2':
        p['status'] = 'closed'
    elif p['id'] == 'phase-3':
        p['status'] = 'active'
        p['goal'] = ('408 DS 自第6讲续排（W35保守基线：集训期无回执，结营实报后前移）；'
                     '9/30 前推进至~第98讲；数学 880 强化刷题；英语真题阅读启动')

# 1b. 生成 phase-3 任务（8/31 - 9/30，31 天 × 3 项/天 = 93 项）
REASON = '2026-08-30 周复盘（W35）：结营零回执，按 W34 预案以最保守基线（王道第5讲）续排 phase-3'
math_titles = [
    '数学强化：李林880 高数刷题（极限+导数章节）',
    '数学强化：李林880 高数刷题（积分+应用章节）',
    '数学强化：李林880 线代刷题（行列式+矩阵章节）',
    '数学强化：880错题整理+回做（先清集训遗留）',
]
start = datetime.date(2026, 8, 31)
new_tasks = []
for i in range(31):
    d = start + datetime.timedelta(days=i)
    day = (d - datetime.date(2026, 7, 31)).days
    ds = d.isoformat()
    lec_a = 6 + 3 * i
    lec_b = 8 + 3 * i
    new_tasks.append({
        'id': f't{next_id}', 'day': day, 'date': ds,
        'title': f'408 DS：王道视频第{lec_a}-{lec_b}讲 + 课后题（保守基线续排）',
        'topic': '数据结构', 'subject': '408', 'phase_id': 'phase-3',
        'estimated_minutes': 120, 'difficulty': 'medium', 'status': 'pending',
        'prerequisites': [], 'actual_minutes': None, 'actual_date': None,
        'mastery': None, 'resource': '王道DS教材', 'output': '',
        'adjustment_reason': REASON,
    })
    next_id += 1
    new_tasks.append({
        'id': f't{next_id}', 'day': day, 'date': ds,
        'title': math_titles[i % 4],
        'topic': '数学', 'subject': '数学', 'phase_id': 'phase-3',
        'estimated_minutes': 180, 'difficulty': 'medium', 'status': 'pending',
        'prerequisites': [], 'actual_minutes': None, 'actual_date': None,
        'mastery': None, 'resource': '李林880', 'output': '',
        'adjustment_reason': REASON,
    })
    next_id += 1
    new_tasks.append({
        'id': f't{next_id}', 'day': day, 'date': ds,
        'title': '英语二真题：阅读理解精读1篇 + Anki新学≈100卡',
        'topic': '阅读+单词', 'subject': '英语', 'phase_id': 'phase-3',
        'estimated_minutes': 90, 'difficulty': 'medium', 'status': 'pending',
        'prerequisites': [], 'actual_minutes': None, 'actual_date': None,
        'mastery': None, 'resource': '英语二真题 + Anki卡片组（4387卡）', 'output': '',
        'adjustment_reason': REASON,
    })
    next_id += 1

tasks.extend(new_tasks)
# 408 续排自检：phase-3 内部连续
p3 = sorted([t for t in tasks if t.get('phase_id') == 'phase-3' and t.get('subject') == '408'],
            key=lambda x: x['date'])
prev_end = 5
ok = True
for t in p3:
    a, b = map(int, t['title'].split('第')[1].split('讲')[0].split('-'))
    if a != prev_end + 1:
        ok = False
        print(f'  !! 408 contiguity break at {t["id"]}: {t["title"]}')
        break
    prev_end = b
print('phase-3 408 contiguity 6->98:', ok, f'(ends {prev_end})')

rm['metadata']['last_review'] = ('2026-08-30: 2026-W35 周复盘（phase-2 closed → phase-3 active；'
                                 'phase-3 任务 t113-t205 保守基线生成；system-state 推进至 8/30）')
atomic_dump(RM, rm)
print(f'roadmap written: total tasks {len(tasks)} (was 112, +{len(new_tasks)})')

# ---------- 2. system-state ----------
ss = load(SS)
ss['current_project']['current_day'] = 30
ss['today_session'] = {
    'date': '2026-08-30',
    'status': 'in_session',
    'actual_minutes_available': 390,
    'started_at': '2026-08-30T09:00:00',
    'current_stage': 'opening',
    'completed_topics': [],
}
# last_session 保持 8/6 真实记录（最后一次真实互动）
ss['updated_at'] = '2026-08-30T10:30:00'
atomic_dump(SS, ss)
print('system-state written: current_day 30, today 2026-08-30')

# ---------- 3. changelog ----------
with open(CL, encoding='utf-8') as f:
    cl = f.read()
entry = ('| 2026-08-30 | 周复盘（2026-W35）：① phase-2（暑期集训期）→ closed（8/27 结营，按日期事实），'
         'phase-3（408攻坚+数学强化）→ active；② 生成 phase-3 任务 93 项（t113-t205，8/31-9/30，每天3项：'
         '408 DS 3讲120min + 数学880 180min + 英语阅读+Anki 90min），408 按 W34 预案以最保守基线'
         '（王道第5讲）自第6讲续排，9/30 推进至~第98讲；③ phase-3 目标文案改保守版；④ system-state 由 8/23 '
         '推进至 8/30（第30天）；⑤ 8/28-8/30 为集训后过渡休息日（已按「暂无安排」提醒），任务自 8/31 起排 '
         '| 8/27 结营后用户零回执（8/28-30 无消息），W34 预案「若仍不回则按最保守基线重排」触发；'
         '改编号=查全链（沿用 8/9 教训），408 续排可随时按用户实报前移 |\n')
with open(CL, 'w', encoding='utf-8') as f:
    f.write(cl + entry)
print('changelog appended')

# ---------- 4. 汇总 ----------
from collections import Counter
print('subjects now:', dict(Counter(t.get('subject') for t in tasks)))
print('phases now:', {p['id']: p['status'] for p in rm['phases']})
print('DONE')
