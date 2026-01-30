# Heal Request: scheduling/events/Events/Schedule Event

> **Generated**: 2026-01-27T19:20:43.472704
> **Test Type**: test
> **Duration**: 68604ms
**Status**: `open`

---

## What Failed

## Config

- **base_url**: `https://www.vcita.com`
- **login_url** (derived): `https://www.vcita.com/login`
- **username**: `itzik+autotest.1769462440@vcita.com`

```
TimeoutError: Locator.wait_for: Timeout 30000ms exceeded.
Call log:
  - waiting for locator("[data-qa=\"VcMenuItem-calendar-subitem-event_list\"]") to be visible
    63 × locator resolved to hidden <div align-center="" data-v-23b36969="" data-v-50fa0c52="" data-qa="VcMenuItem-calendar-subitem-event_list" class="layout align-center VcMenuItem-subitem VcMenuItem-userSelectNone ps-6 md desktop">…</div>

```

**Error Type**: `TimeoutError`

## Test Location

Test files are located at: `C:\Programming\auto_tester\tests\scheduling\events\schedule_event`

- `steps.md` - Test steps and requirements
- `script.md` - Test script and flow
- `test.py` - Test implementation code
- `changelog.md` - History of previous fixes

## Screenshot

Screenshot saved at: `.temp_screenshots\schedule_event_20260127_192043.png`

**Analyze the screenshot to understand the UI state at failure.**

## Context Summary

Context had 12 keys: base_url, created_client_email, created_client_id, created_client_name, event_client_email, event_client_id, event_client_name, event_group_service_name, logged_in_user, password, scheduled_event_time, username

Full context is available in the test run artifacts.

---

## Next Steps

1. Review the error message above
2. Check the screenshot to see the UI state
3. Read the test files at the location above
4. Review changelog.md for previous fixes
5. Use Playwright MCP to debug if needed

See `.cursor/rules/heal.mdc` for detailed healing process.