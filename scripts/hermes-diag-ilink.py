#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""iLink 诊断探测 (2026-09-10, W37 周复盘用).
发送一条真实诊断消息 + 一次 getupdates 探测, 输出原始响应.
不经过 gateway 熔断器/适配器 (独立通道, 复刻 _api_post).
用法: python3 hermes-diag-ilink.py [--send-only|--updates-only]
"""
import base64, json, secrets, struct, sys, time, urllib.request

ENV_PATH = "/root/.hermes/profiles/408-study/.env"
ILINK_APP_ID = "bot"
CHANNEL_VERSION = "2.2.0"
ILINK_APP_CLIENT_VERSION = str((2 << 16) | (2 << 8) | 0)
ITEM_TEXT = 1
MSG_TYPE_BOT = 2
MSG_STATE_FINISH = 2


def load_env(path):
    d = {}
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            d[k.strip()] = v.strip()
    return d


def random_wechat_uin():
    value = struct.unpack(">I", secrets.token_bytes(4))[0]
    return base64.b64encode(str(value).encode("utf-8")).decode("ascii")


def build_headers(token, body):
    body_len = len(body) if isinstance(body, bytes) else len(body.encode("utf-8"))
    return {
        "Content-Type": "application/json",
        "AuthorizationType": "ilink_bot_token",
        "Content-Length": str(body_len),
        "X-WECHAT-UIN": random_wechat_uin(),
        "iLink-App-Id": ILINK_APP_ID,
        "iLink-App-ClientVersion": ILINK_APP_CLIENT_VERSION,
        "Authorization": f"Bearer {token}",
    }


def api_post(base_url, endpoint, payload, token, timeout=15):
    body = json.dumps({**payload, "base_info": {"channel_version": CHANNEL_VERSION}})
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/{endpoint}", data=body.encode("utf-8"),
        headers=build_headers(token, body), method="POST")
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", "replace")
            return {"http": resp.status, "ms": int((time.time()-t0)*1000), "raw": raw[:600]}
    except Exception as e:
        body_txt = ""
        if hasattr(e, "read"):
            try: body_txt = e.read().decode("utf-8", "replace")[:600]
            except Exception: pass
        return {"http": getattr(e, "code", "EXC"), "ms": int((time.time()-t0)*1000),
                "raw": body_txt, "exc": str(e)[:200]}


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "both"
    env = load_env(ENV_PATH)
    account_id = env.get("WEIXIN_ACCOUNT_ID", "")
    token = env.get("WEIXIN_TOKEN", "")
    base_url = env.get("WEIXIN_BASE_URL", "")
    to = env.get("WEIXIN_HOME_CHANNEL", "")
    print(f"[probe] account={account_id[:12]}... base={base_url} to={to[:16]}...")

    if mode in ("both", "updates-only"):
        print("\n--- getupdates (读通道探测) ---")
        r = api_post(base_url, "ilink/bot/getupdates",
                     {"get_updates_buf": ""}, token)
        print(json.dumps(r, ensure_ascii=False, indent=1))

    if mode in ("both", "send-only"):
        print("\n--- sendmessage (写通道探测, 真实发送 1 条) ---")
        text = "[诊断-可忽略] 系统自检: 投递通道测试, 如收到本条请勿回复. (W37周复盘)"
        message = {
            "from_user_id": "", "to_user_id": to, "client_id": account_id,
            "message_type": MSG_TYPE_BOT, "message_state": MSG_STATE_FINISH,
            "item_list": [{"type": ITEM_TEXT, "text_item": {"text": text}}],
        }
        r = api_post(base_url, "ilink/bot/sendmessage", {"msg": message}, token)
        print(json.dumps(r, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
