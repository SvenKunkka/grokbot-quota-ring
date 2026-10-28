<!-- SVENKUNKKA-README-NAV:BEGIN -->
[English overview](#project-overview-en) · [中文项目说明](#project-overview-zh) · [Maintainer on X / 维护者 X](https://x.com/Svenu1s5)
<!-- SVENKUNKKA-README-NAV:END -->

# grokbot-quota-ring

A [SwiftBar](https://github.com/swiftbar/SwiftBar) plugin that shows your remaining Grok Bot weekly quota as a small filled pie in the macOS menu bar. It shows no text or percentage in the bar itself.

- Full green disc = full quota; the pie (clockwise from 12 o'clock) shrinks and shifts green → yellow → red as quota drains.
- Empty gray outline = no quota (or not authorized yet).
- Dimmed pie = last fetch failed; the dropdown shows the last value and when it was fetched.
- Dropdown: remaining %, reset time, refresh, link to the usage page.

## Install
```bash
brew install --cask swiftbar
/usr/bin/python3 -m pip install --user pillow
mkdir -p ~/SwiftBarPlugins/.grokbot-quota
cp quota.5m.py ~/SwiftBarPlugins/ && cp setup.sh ~/SwiftBarPlugins/.grokbot-quota/
```
Point SwiftBar's plugin folder at `~/SwiftBarPlugins`. Refreshes every 5 minutes (from the file name).

## Authorize
Run `bash ~/SwiftBarPlugins/.grokbot-quota/setup.sh` and paste your cursor.com session (the `WorkosCursorSessionToken` cookie value, or the full Cookie header). Input is hidden. It is stored only in the macOS Keychain (service `grokbot-quota`). The plugin never reads browser cookie files and the repo contains no secrets.

Without Keychain access you can write `~/.grokbot-quota/manual.json` yourself: `{"remaining": 80, "reset": "2026-10-19T00:00:00Z"}`.

## Data source (undocumented)
`POST https://cursor.com/api/dashboard/get-sand-usage-status` with body `{}`, `Origin: https://cursor.com` and the session cookie. **This endpoint is undocumented and may change or break at any time.** Credit: discovered and used in [CodexBar PR #3127](https://github.com/steipete/CodexBar/pull/3127) (MIT). The ring is drawn only when `hasNonZeroIncludedLimit` is true, `includedLimitZero` and `usesPooledEnterpriseAllowance` are not true, and `usagePercent` is present. Otherwise an account with no allowance would show a full green ring.

Test without network: `GROKBOT_QUOTA_FAKE=60 python3 quota.5m.py` (or `0`, `fail:40`).

## License
MIT
![states](docs/preview.png)


---

<!-- SVENKUNKKA-PROJECT-INFO:BEGIN -->

<a id="project-overview-zh"></a>
## 中文项目说明

macOS SwiftBar 插件，以菜单栏饼图显示 Grok Bot 每周剩余额度；颜色与扇区随额度变化，下拉菜单显示剩余比例、重置时间和最近获取状态。

**使用入口：** 安装 SwiftBar 与 Pillow，将 `quota.5m.py` 放入插件目录；安装、授权和手动数据模式见原说明，可用 `GROKBOT_QUOTA_FAKE=60 python3 quota.5m.py` 离线预览。

**范围说明：** 依赖 cursor.com 未公开接口，可能随服务变化失效；授权信息按原流程保存在 macOS 钥匙串。

<a id="project-overview-en"></a>
## English project overview

A macOS SwiftBar plugin that shows remaining weekly Grok Bot quota as a menu-bar pie chart. Color and area change with usage; the dropdown includes remaining quota, reset time, and fetch status.

**Getting started:** Install SwiftBar and Pillow and place `quota.5m.py` in the plugin folder. See the original README for installation, authorization, and manual-data mode; preview offline with `GROKBOT_QUOTA_FAKE=60 python3 quota.5m.py`.

**Scope:** Depends on an undocumented cursor.com endpoint that may change or break. The documented authorization flow stores credentials in macOS Keychain.

**仓库维护者 / Repository maintainer:** [SvenKunkka](https://github.com/SvenKunkka) · [X / Twitter](https://x.com/Svenu1s5)

<!-- SVENKUNKKA-PROJECT-INFO:END -->
