# Heal Request: scheduling/services/Services/Create Service

> **Generated**: 2026-01-31T14:55:24.219920
> **Test Type**: test
> **Duration**: 26302ms
**Status**: `open`

---

## What Failed

```
TimeoutError: Locator.wait_for: Timeout 15000ms exceeded.
Call log:
  - waiting for locator("iframe[title=\"angularjs\"]").content_frame.get_by_role("dialog") to be hidden
    33 × locator resolved to visible <md-dialog role="dialog" tabindex="-1" aria-label="Service info ..." aria-describedby="dialogContent_52" class="new-service-dialog _md md-transition-in">…</md-dialog>

```

**Error Type**: `TimeoutError`

## Test Location

Test files are located at: `C:\Programming\auto_tester\tests\scheduling\services\create_service`

- `steps.md` - Test steps and requirements
- `script.md` - Test script and flow
- `test.py` - Test implementation code
- `changelog.md` - History of previous fixes

## Screenshot

Screenshot saved at: `.temp_screenshots\create_service_20260131_145523.png`

**Analyze the screenshot to understand the UI state at failure.**

## Context Summary

Context had 1 keys: logged_in_user

Full context is available in the test run artifacts.

---

## Next Steps

1. Review the error message above
2. Check the screenshot to see the UI state
3. Read the test files at the location above
4. Review changelog.md for previous fixes
5. Use Playwright MCP to debug if needed

See `.cursor/rules/heal.mdc` for detailed healing process.