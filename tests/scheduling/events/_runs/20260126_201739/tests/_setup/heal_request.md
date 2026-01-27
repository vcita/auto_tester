# Heal Request: scheduling/events/Events/_setup

> **Generated**: 2026-01-26T20:18:31.476056
> **Test Type**: setup
> **Duration**: 26738ms
**Status**: `open`

---

## What Failed

## Config

- **base_url**: `https://www.vcita.com`
- **login_url** (derived): `https://www.vcita.com/login`
- **username**: `itzik+autotest.1769433641@vcita.com`

```
TimeoutError: Locator.wait_for: Timeout 15000ms exceeded.
Call log:
  - waiting for locator("iframe[title=\"angularjs\"]").content_frame.get_by_role("dialog") to be hidden
    4 × locator resolved to visible <md-dialog role="dialog" tabindex="-1" aria-label="Service info ..." aria-describedby="dialogContent_92" class="new-service-dialog _md md-transition-in">…</md-dialog>
    2 × locator resolved to visible <md-dialog role="dialog" tabindex="-1" aria-label="Service info ..." aria-describedby="dialogContent_92" class="new-service-dialog _md md-transition-out-add md-transition-in-remove md-transition-out md-transition-out-add-active md-transition-in-remove-active">…</md-dialog>
    - locator resolved to visible <md-dialog role="dialog" tabindex="-1" aria-label="Great. Now ..." aria-describedby="dialogContent_170" class="new-event-prompt _md md-transition-in-add md-transition-out-remove md-transition-in md-transition-in-add-active md-transition-out-remove-active">…</md-dialog>
    25 × locator resolved to visible <md-dialog role="dialog" tabindex="-1" aria-label="Great. Now ..." aria-describedby="dialogContent_170" class="new-event-prompt _md md-transition-in">…</md-dialog>

```

**Error Type**: `TimeoutError`

## Test Location

Test files are located at: `C:\Programming\auto_tester\tests\scheduling\events\_setup`

- `steps.md` - Test steps and requirements
- `script.md` - Test script and flow
- `test.py` - Test implementation code
- `changelog.md` - History of previous fixes

## Screenshot

Screenshot saved at: `.temp_screenshots\_setup_20260126_201831.png`

**Analyze the screenshot to understand the UI state at failure.**

## Context Summary

Context had 4 keys: base_url, logged_in_user, password, username

Full context is available in the test run artifacts.

---

## Next Steps

1. Review the error message above
2. Check the screenshot to see the UI state
3. Read the test files at the location above
4. Review changelog.md for previous fixes
5. Use Playwright MCP to debug if needed

See `.cursor/rules/heal.mdc` for detailed healing process.