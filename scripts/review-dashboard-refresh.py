#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-W32 周复盘：刷新 dashboard-data.json（原子写入）
口径：completed=0（本周无回写）；overdue=date<今天且未完成且未归档；phase-1 closed / phase-2 active
"""
import json, os, datetime

RM = '/root/27-study/状态数据/roadmap.json'
DB = '/root/27-study/状态数据/dashboard-data.json'

with open(RM, encoding='utf-8') as f:
    rm = json.load(f)

today = '2026-08-09'
tasks = rm['tasks']
total = len(tasks)
completed = sum(1 for t in tasks if t.get('status') == 'completed')
pending = total - completed
overdue = sum(1 for t in tasks
              if (t.get('date') or '') < today
              and t.get('status') != 'completed'
              and not t.get('archived'))

# 科目统计（含已归档，与旧口径一致）
subjects = {}
for t in tasks:
    s = t.get('subject', '综合')
    d = subjects.setdefault(s, {'total_tasks': 0, 'completed_tasks': 0, 'pending_tasks': 0})
    d['total_tasks'] += 1
    if t.get('status') == 'completed':
        d['completed_tasks'] += 1
    else:
        d['pending_tasks'] += 1
for d in subjects.values():
    d['completion_percentage'] = round(d['completed_tasks'] / d['total_tasks'] * 100) if d['total_tasks'] else 0

phase_map = {p['id']: p for p in rm['phases']}
phases = {}
for pid in ['phase-1', 'phase-2', 'phase-3', 'phase-4', 'phase-5']:
    p = phase_map[pid]
    phases[pid] = {
        'title': p['title'],
        'status': p['status'],
        'date_range': p['date_range'],
        'total_days': p['days'],
        'completed_percentage': 0,
    }

db = {
    'dashboard_version': '1.0.0',
    'generated_at': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    'summary': {
        'total_study_minutes': 0,
        'consecutive_days': 0,
        'completion_rate': round(completed / total * 100) if total else 0,
        'error_count': 0,
    },
    'progress': {
        'current_cycle': '27考研',
        'cycle_start_date': '2026-07-31',
        'total_cycle_days': 148,
        'current_day': 9,
        'days_remaining': 139,
        'progress_percentage': round(9 / 148 * 100),
    },
    'tasks': {
        'total_tasks': total,
        'pending_tasks': pending,
        'completed_tasks': completed,
        'overdue_tasks': overdue,
    },
    'subjects': subjects,
    'phases': phases,
    'recent_activities': {
        'last_session_date': '2026-08-06',
        'last_session_minutes': None,
        'last_topic_completed': None,
        'last_update': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    },
    'status': 'in_session',
}

tmp = DB + '.tmp'
with open(tmp, 'w', encoding='utf-8') as f:
    json.dump(db, f, ensure_ascii=False, indent=1)
os.replace(tmp, DB)

with open(DB, encoding='utf-8') as f:
    chk = json.load(f)
print('total:', chk['tasks']['total_tasks'], 'pending:', chk['tasks']['pending_tasks'],
      'completed:', chk['tasks']['completed_tasks'], 'overdue:', chk['tasks']['overdue_tasks'])
print('subjects:', {k: v['total_tasks'] for k, v in chk['subjects'].items()})
print('phases:', {k: v['status'] for k, v in chk['phases'].items()})
print('progress:', chk['progress']['current_day'], chk['progress']['days_remaining'], chk['progress']['progress_percentage'])
print('generated_at:', chk['generated_at'])
