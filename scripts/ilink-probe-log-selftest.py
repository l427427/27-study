#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ilink-probe-log.py 的 stub harness（零网络流量，验证分支真的被走到）。

做法：造两个假的「探测脚本」（各自在被调用时写一个 marker 文件 + 打印假响应），
用 ILINK_PROBE_CMD 指向它们，ILINK_DIAG_LOG 指向临时文件，断言：
  1. 每一次 stub 都真的被执行了（marker 文件存在 = 探测命令真被调用）
  2. 结果被追加进日志（保留原有行，新增 1 行）
  3. 故障签名 → 「未恢复」；恢复签名 → 「通道恢复」
运行：python3 ilink-probe-log-selftest.py
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
WRAP = os.path.join(HERE, "ilink-probe-log.py")
PY = sys.executable or "python3"

FAIL_OUT = (
    "[probe] account=c8aa1a7a2a7b... base=https://ilinkai.weixin.qq.com to=o9cq80xXfVrX59q6...\n\n"
    "--- sendmessage (写通道探测, 真实发送 1 条) ---\n{\n \"http\": 200,\n \"ms\": 796,\n"
    " \"raw\": \"{\\\"ret\\\":-2,\\\"errmsg\\\":\\\"prepare failed\\\"}\"\n}\n")
OK_OUT = (
    "[probe] account=c8aa1a7a2a7b... base=https://ilinkai.weixin.qq.com to=o9cq80xXfVrX59q6...\n\n"
    "--- sendmessage (写通道探测, 真实发送 1 条) ---\n{\n \"http\": 200,\n \"ms\": 640,\n"
    " \"raw\": \"{\\\"ret\\\":0,\\\"errmsg\\\":\\\"ok\\\"}\"\n}\n")

tmpdir = tempfile.mkdtemp(prefix="ilinkprobe-selftest-")
results = []


def case(name, out_text, expect):
    marker = os.path.join(tmpdir, "marker-%s" % name)
    stub = os.path.join(tmpdir, "stub_probe_%s.py" % name)
    with open(stub, "w", encoding="utf-8") as f:
        f.write("open(%r, 'w').write('called')\n" % marker)
        f.write("print(%r)\n" % out_text)
    log = os.path.join(tmpdir, "diag-%s.log" % name)
    with open(log, "w", encoding="utf-8") as f:
        f.write("PRE-EXISTING LINE\n")
    env = dict(os.environ)
    env["ILINK_PROBE_CMD"] = "%s %s" % (PY, stub)
    env["ILINK_DIAG_LOG"] = log
    env["ILINK_PROBE_NOTE"] = "selftest"
    p = subprocess.Popen([PY, "-u", WRAP], stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, env=env)
    out = p.communicate()[0].decode("utf-8", "replace")
    body = open(log, encoding="utf-8").read()
    lines = [x for x in body.splitlines() if x.strip()]
    new = lines[1] if len(lines) > 1 else ""
    results.append(("%s: stub 真被执行(marker 存在)" % name, os.path.isfile(marker)))
    results.append(("%s: 日志为追加非覆盖" % name, bool(lines) and lines[0] == "PRE-EXISTING LINE"))
    results.append(("%s: 新增 1 行" % name, len(lines) == 2))
    results.append(("%s: 判定=%s" % (name, expect), expect in new))
    results.append(("%s: 备注写入" % name, "selftest" in new))
    results.append(("%s: 退出码 0(不造 job 级报错)" % name, p.returncode == 0))
    print("  [--] %s -> %s" % (name, new or "(no new line)"))


case("fail", FAIL_OUT, "未恢复")
case("ok", OK_OUT, "通道恢复")

ok = all(c[1] for c in results)
for n, c in results:
    print(("PASS" if c else "FAIL"), "-", n)
print("RESULT:", "ALL PASS" if ok else "HAS FAILURES", "(stub harness, 零网络流量)")
sys.exit(0 if ok else 1)
