#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""W38 正式版复盘 · 采集 #4：roadmap-changelog 尾部（只读）"""
P = '/root/27-study/状态数据/roadmap-changelog.md'
txt = open(P, encoding='utf-8').read()
print('bytes=', len(txt), 'lines=', txt.count('\n') + 1)
print('--- 最后 2500 字符 ---')
print(txt[-2500:])
