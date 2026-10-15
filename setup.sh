#!/bin/bash
# Store your Cursor session in the macOS Keychain for grokbot-quota-ring. Input is hidden.
SERVICE="${GROKBOT_QUOTA_SERVICE:-grokbot-quota}"
echo "请粘贴 cursor.com 的登录凭证（WorkosCursorSessionToken 的值，或整段 Cookie），输入不显示，回车结束："
read -rs TOKEN; echo
[ -z "$TOKEN" ] && { echo "未输入，已取消"; exit 1; }
security add-generic-password -U -a "$USER" -s "$SERVICE" -w "$TOKEN" && echo "已保存到钥匙串（$SERVICE）。菜单栏圆环几秒后刷新。"
unset TOKEN
open -g "swiftbar://refreshallplugins" 2>/dev/null || true
