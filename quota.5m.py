#!/usr/bin/env python3
# <xbar.title>Grok Bot Quota Ring</xbar.title>
# <xbar.desc>Menu-bar ring showing remaining Grok Bot weekly quota.</xbar.desc>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
import base64, io, json, os, subprocess, sys, time, urllib.request, datetime

SERVICE = os.environ.get("GROKBOT_QUOTA_SERVICE", "grokbot-quota")
STATE_DIR = os.path.expanduser("~/.grokbot-quota")
CACHE = os.path.join(STATE_DIR, "cache.json")
MANUAL = os.path.join(STATE_DIR, "manual.json")  # {"remaining": 0-100, "reset": "ISO time"}
URL = "https://cursor.com/api/dashboard/get-sand-usage-status"
USAGE_PAGE = "grokbot://app/v1/settings?id=usage"
SETUP = os.path.expanduser("~/SwiftBarPlugins/.grokbot-quota/setup.sh")

GREEN, YELLOW, RED, GRAY = (0x34, 0xC7, 0x59), (0xFF, 0xCC, 0x00), (0xFF, 0x3B, 0x30), (0x8E, 0x8E, 0x93)

def lerp(a, b, t): return tuple(round(x + (y - x) * t) for x, y in zip(a, b))

def color_for(rem):
    f = max(0.0, min(1.0, rem / 100.0))
    return lerp(RED, YELLOW, f / 0.5) if f < 0.5 else lerp(YELLOW, GREEN, (f - 0.5) / 0.5)

def ring_png(rem, dim=False, size=36):
    from PIL import Image, ImageDraw
    S = size * 4  # supersample
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    w = int(S * 0.13); pad = w // 2 + 4
    box = [pad, pad, S - pad, S - pad]
    alpha = 110 if dim else 255
    if rem is None or rem <= 0:
        d.ellipse(box, outline=GRAY + (alpha,), width=max(4, w // 3))
    else:
        c = color_for(rem)
        d.ellipse(box, outline=c + (60 if not dim else 35,), width=w)  # faint track
        if rem >= 99.5:
            d.ellipse(box, outline=c + (alpha,), width=w)
        else:
            d.arc(box, -90, -90 + 360 * rem / 100.0, fill=c + (alpha,), width=w)
    img = img.resize((size, size), Image.LANCZOS)
    buf = io.BytesIO(); img.save(buf, "PNG"); return buf.getvalue()

def keychain_cookie():
    try:
        r = subprocess.run(["security", "find-generic-password", "-s", SERVICE, "-w"],
                           capture_output=True, text=True, timeout=10)
        v = r.stdout.strip()
        return v or None
    except Exception:
        return None

def fetch(cookie):
    if "=" not in cookie:
        cookie = "WorkosCursorSessionToken=" + cookie
    req = urllib.request.Request(URL, data=b"{}", method="POST", headers={
        "Content-Type": "application/json", "Origin": "https://cursor.com",
        "Cookie": cookie, "User-Agent": "grokbot-quota-ring/1.0"})
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k): return None
    opener = urllib.request.build_opener(NoRedirect)
    with opener.open(req, timeout=8) as r:
        return json.loads(r.read().decode())

def parse(resp):
    """Return (status, remaining, reset_iso). status: ok|not_included|unreadable"""
    r = resp.get("usageStatus", resp) if isinstance(resp, dict) else {}
    flags = ("usesPooledEnterpriseAllowance", "includedLimitZero", "hasNonZeroIncludedLimit")
    if not any(k in r for k in flags + ("usagePercent",)):
        return "unreadable", None, None
    if r.get("usesPooledEnterpriseAllowance") is True or r.get("includedLimitZero") is True \
            or r.get("hasNonZeroIncludedLimit") is not True:
        return "not_included", None, None
    if r.get("usagePercent") is None:
        return "unreadable", None, None
    rem = max(0.0, min(100.0, 100.0 - float(r["usagePercent"])))
    reset = r.get("nextResetTimestampUtc")
    if not reset and r.get("currentPeriodStart"):
        try:
            v = r["currentPeriodStart"]
            st = datetime.datetime.fromtimestamp(int(v) / 1000, datetime.timezone.utc) if str(v).isdigit() \
                else datetime.datetime.fromisoformat(str(v).replace("Z", "+00:00"))
            reset = (st + datetime.timedelta(days=7)).isoformat()
        except Exception:
            reset = None
    elif reset and str(reset).isdigit():
        reset = datetime.datetime.fromtimestamp(int(reset) / 1000, datetime.timezone.utc).isoformat()
    return "ok", rem, reset

def fmt_time(iso):
    if not iso: return "未知"
    try:
        return datetime.datetime.fromisoformat(str(iso).replace("Z", "+00:00")).astimezone().strftime("%m-%d %H:%M")
    except Exception:
        return str(iso)

def load(p):
    try:
        with open(p) as f: return json.load(f)
    except Exception: return None

def save_cache(d):
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(CACHE, "w") as f: json.dump(d, f)

def render(rem, dim, lines):
    b64 = base64.b64encode(ring_png(rem, dim)).decode()
    print(f"| image={b64}")
    print("---")
    for l in lines: print(l)
    print("---")
    print("立即刷新 | refresh=true")
    print(f"打开用量页面 | href={USAGE_PAGE}")

def main():
    fake = os.environ.get("GROKBOT_QUOTA_FAKE")  # testing: "75", "0", "fail:40"
    now = time.strftime("%H:%M")
    if fake is not None:
        if fake.startswith("fail:"):
            return render(float(fake[5:]), True, [f"获取失败，显示上次数据（更新于 {now}）"])
        v = float(fake); return render(v, False, [f"剩余额度：{v:.0f}%"])
    cookie = keychain_cookie()
    if not cookie:
        m = load(MANUAL)
        if m and m.get("remaining") is not None:
            v = float(m["remaining"])
            return render(v, False, [f"剩余额度：{v:.0f}%（手动填写）", f"重置时间：{fmt_time(m.get('reset'))}",
                                     "未授权：在终端运行下面的授权脚本即可自动获取"])
        return render(None, False, ["未授权，暂无额度数据",
                                    f"点此授权（在终端粘贴登录凭证） | bash={SETUP} terminal=true",
                                    f"或手动填写：编辑 {MANUAL}"])
    try:
        status, rem, reset = parse(fetch(cookie))
    except Exception as e:
        status, rem, reset, err = "error", None, None, type(e).__name__
    if status == "ok":
        save_cache({"remaining": rem, "reset": reset, "updated": now})
        return render(rem, False, [f"剩余额度：{rem:.0f}%", f"重置时间：{fmt_time(reset)}", f"更新于 {now}"])
    c = load(CACHE) or {}
    reason = {"not_included": "当前账号不含 Grok Bot 额度", "unreadable": "接口返回无法识别",
              "error": "网络或登录失效"}[status]
    return render(c.get("remaining"), True, [f"获取失败：{reason}",
                  f"上次数据：{c['remaining']:.0f}%（更新于 {c.get('updated')}）" if c.get("remaining") is not None else "暂无历史数据",
                  f"重新授权 | bash={SETUP} terminal=true"])

if __name__ == "__main__":
    main()
