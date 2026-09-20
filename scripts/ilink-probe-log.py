#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""iLink 每日出站探测 + 自动落日志（2026-09-20 W38 正式版复盘新增）。

做两件事：
  1. 调用 hermes-diag-ilink.py send-only（绕开 gateway 熔断，独立通道）
  2. 把结果解析成一行，追加写入 ilink-diag.log

用法（cron 里固定一条命令，末尾不拼东西）：
  cd /root/27-study/scripts && python3 -u ilink-probe-log.py 2>&1 | head

测试用环境变量（生产不用设）：
  ILINK_PROBE_CMD  覆盖探测命令（stub harness 用）
  ILINK_DIAG_LOG   覆盖日志路径
  ILINK_PROBE_NOTE 覆盖备注文字
"""
import datetime
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROBE = os.path.join(HERE, "hermes-diag-ilink.py")
LOG = os.environ.get("ILINK_DIAG_LOG", os.path.join(HERE, "ilink-diag.log"))
NOTE = os.environ.get("ILINK_PROBE_NOTE", "")


def run_probe():
    """跑探测，返回 (stdout_text, returncode)。"""
    cmd = os.environ.get("ILINK_PROBE_CMD")
    if cmd:
        argv = cmd.split()
    else:
        argv = [sys.executable or "python3", "-u", PROBE, "send-only"]
    try:
        p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = p.communicate()[0]
        return out.decode("utf-8", "replace"), p.returncode
    except Exception as e:
        return "[probe-error] %s" % e, -1


def parse(out):
    """提取 http / ms / ret / errmsg。"""
    d = {"http": "?", "ms": "?", "ret": "?", "errmsg": ""}
    m = re.search(r'"http"\s*:\s*("?[^",\n]+"?)', out)
    if m:
        d["http"] = m.group(1).strip('"')
    m = re.search(r'"ms"\s*:\s*(\d+)', out)
    if m:
        d["ms"] = m.group(1)
    m = re.search(r"ret\\?\"\s*:\s*(-?\d+)", out)
    if m:
        d["ret"] = m.group(1)
    m = re.search(r'errmsg\\?\"\s*:\s*\\?"([^"\\]+)', out)
    if m:
        d["errmsg"] = m.group(1)
    recovered = (d["http"] == "200") and ("prepare failed" not in out) and ("ret\":-2" not in out.replace(" ", ""))
    d["recovered"] = "yes" if recovered else "no"
    return d


def append_log(line):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def main():
    out, rc = run_probe()
    d = parse(out)
    recovered = d.get("recovered") == "yes"
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    verdict = "通道恢复(可补发积压)" if recovered else "未恢复(签名不变)"
    line = "%s | send-only | http=%s ms=%s ret=%s %s | %s%s" % (
        stamp, d["http"], d["ms"], d["ret"], d["errmsg"],
        verdict, (" | " + NOTE) if NOTE else "")
    append_log(line)
    print(line)
    print("rc=%s recovered=%s log=%s" % (rc, recovered, LOG))
    # 探测失败/异常也让 job 正常结束（不制造 job 级报错），恢复与否由日志判定
    return 0


if __name__ == "__main__":
    sys.exit(main())
