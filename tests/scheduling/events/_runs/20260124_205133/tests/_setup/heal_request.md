# Heal Request: scheduling/events/Events/_setup

> **Generated**: 2026-01-24T20:52:47.624449
> **Test Type**: setup
> **Duration**: 34902ms
**Status**: `open`

---

## What Failed

```
TimeoutError: Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for locator("iframe[title=\"angularjs\"]").content_frame.get_by_role("button", name="Define the services your")

```

**Error Type**: `TimeoutError`

## Test Location

Test files are located at: `C:\Programming\auto_tester\tests\scheduling\events\_setup`

- `steps.md` - Test steps and requirements
- `script.md` - Test script and flow
- `test.py` - Test implementation code
- `changelog.md` - History of previous fixes

## Screenshot

Screenshot saved at: `.temp_screenshots\_setup_20260124_205247.png`

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