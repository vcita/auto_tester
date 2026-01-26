# Heal Request: scheduling/events/Events/Schedule Event

> **Generated**: 2026-01-25T22:19:19.516940
> **Test Type**: test
> **Duration**: 33703ms
**Status**: `open`

---

## What Failed

```
TimeoutError: Locator.wait_for: Timeout 30000ms exceeded.
Call log:
  - waiting for locator("iframe[title=\"angularjs\"]").content_frame.locator("#vue_iframe_layout").content_frame.get_by_role("option").filter(has_text="Event Test Workshop 1769372292").first to be visible

```

**Error Type**: `TimeoutError`

## Test Location

Test files are located at: `C:\Programming\auto_tester\tests\scheduling\events\schedule_event`

- `steps.md` - Test steps and requirements
- `script.md` - Test script and flow
- `test.py` - Test implementation code
- `changelog.md` - History of previous fixes

## Screenshot

Screenshot saved at: `.temp_screenshots\schedule_event_20260125_221919.png`

**Analyze the screenshot to understand the UI state at failure.**

## Context Summary

Context had 8 keys: created_client_email, created_client_id, created_client_name, event_client_email, event_client_id, event_client_name, event_group_service_name, logged_in_user

Full context is available in the test run artifacts.

---

## Next Steps

1. Review the error message above
2. Check the screenshot to see the UI state
3. Read the test files at the location above
4. Review changelog.md for previous fixes
5. Use Playwright MCP to debug if needed

See `.cursor/rules/heal.mdc` for detailed healing process.