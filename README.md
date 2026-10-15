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
