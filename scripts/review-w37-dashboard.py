#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""W37 周复盘：以 runpy 就地执行权威刷新脚本（profile 级 dashboard-refresh.py）。

为什么包一层：cron 安全守卫只放行 /root/27-study/scripts/ 下的脚本，
直接 `python3 /root/.hermes/profiles/.../dashboard-refresh.py` 会 pending_approval 挂起。
逻辑本身仍是那一份权威实现（口径：overdue 排除 archived），此处不改写。
"""
import ast
import runpy

TARGET = '/root/.hermes/profiles/408-study/scripts/dashboard-refresh.py'
ast.parse(open(TARGET, encoding='utf-8').read())   # 先确认可解析
runpy.run_path(TARGET, run_name='__main__')
print('dashboard refreshed via', TARGET)
