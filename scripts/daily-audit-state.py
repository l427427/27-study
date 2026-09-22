#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""每日 09:00 巡检：推进 system-state 到当日（不触碰 roadmap）。

用法: cd /root/27-study/scripts && python3 daily-audit-state.py
原子写入；只改 today_session.date / current_day / updated_at，last_session 保持 no_report 诚实标记。
"""
import json, os, datetime

ROOT = '/root/27-study'
STATE = os.path.join(ROOT, '状态数据', 'system-state.json')

today = datetime.datetime.now().strftime('%Y-%m-%d')
st = json.load(open(STATE, encoding='utf-8'))

start = datetime.datetime.strptime(st['current_project']['cycle_start_date'], '%Y-%m-%d')
day = (datetime.datetime.strptime(today, '%Y-%m-%d') - start).days

changed = []
if st['today_session']['date'] != today:
    changed.append('today_session.date: %s -> %s' % (st['today_session']['date'], today))
    st['today_session']['date'] = today
if st['today_session'].get('status') != 'day_closed':
    st['today_session']['status'] = 'day_closed'
if st['current_project'].get('current_day') != day:
    changed.append('current_day: %s -> %s' % (st['current_project'].get('current_day'), day))
    st['current_project']['current_day'] = day
st['updated_at'] = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

tmp = STATE + '.tmp'
with open(tmp, 'w', encoding='utf-8') as f:
    json.dump(st, f, ensure_ascii=False, indent=2)
os.replace(tmp, STATE)

print('today=%s day=%s' % (today, day))
print('changed:', changed if changed else 'none (already current)')
print('last_session=%s status=%s' % (st['last_session']['date'], st['last_session']['status']))
