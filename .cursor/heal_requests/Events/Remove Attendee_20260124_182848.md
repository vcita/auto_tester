# Heal Request: scheduling/events/Events/Remove Attendee

> **Generated**: 2026-01-24T18:28:48.301007
> **Test Type**: test
> **Duration**: 10698ms
**Status**: `open`

---

## What Failed

```
TimeoutError: Locator.wait_for: Timeout 10000ms exceeded.
Call log:
  - waiting for locator("iframe[title=\"angularjs\"]").content_frame.locator("#vue_iframe_layout").content_frame.get_by_text("Event TestClient1769272052").locator("..").locator("..").locator("button").nth(1) to be visible
    24 × locator resolved to hidden <button type="button" data-v-76a5b8fc="" class="three-dots activator-container v-btn v-btn--flat v-btn--icon v-btn--round v-btn--text theme--light v-size--default">…</button>

```

**Error Type**: `TimeoutError`

## Test Location

Test files are located at: `C:\Programming\auto_tester\tests\scheduling\events\remove_attendee`

- `steps.md` - Test steps and requirements
- `script.md` - Test script and flow
- `test.py` - Test implementation code
- `changelog.md` - History of previous fixes

## Screenshot

Screenshot saved at: `.temp_screenshots\remove_attendee_20260124_182848.png`

**Analyze the screenshot to understand the UI state at failure.**

## Context Summary

Context had 11 keys: created_client_email, created_client_id, created_client_name, event_attendee_id, event_client_email, event_client_id, event_client_name, event_group_service_name, logged_in_user, scheduled_event_id, scheduled_event_time

Full context is available in the test run artifacts.

---

## Next Steps

1. Review the error message above
2. Check the screenshot to see the UI state
3. Read the test files at the location above
4. Review changelog.md for previous fixes
5. Use Playwright MCP to debug if needed

See `.cursor/rules/heal.mdc` for detailed healing process.