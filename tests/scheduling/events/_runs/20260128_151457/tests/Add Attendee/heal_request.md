# Heal Request: scheduling/events/Events/Add Attendee

> **Generated**: 2026-01-28T15:19:13.529384
> **Test Type**: test
> **Duration**: 20328ms
**Status**: `open`

---

## What Failed

## Config

- **base_url**: `https://www.vcita.com`
- **login_url** (derived): `https://www.vcita.com/login`
- **username**: `itzik+autotest.1769462440@vcita.com`

```
TimeoutError: Locator.wait_for: Timeout 10000ms exceeded.
Call log:
  - waiting for locator("iframe[title=\"angularjs\"]").content_frame.get_by_role("button", name="Send") to be visible

```

**Error Type**: `TimeoutError`

## Test Location

Test files are located at: `C:\Programming\auto_tester\tests\scheduling\events\add_attendee`

- `steps.md` - Test steps and requirements
- `script.md` - Test script and flow
- `test.py` - Test implementation code
- `changelog.md` - History of previous fixes

## Screenshot

Screenshot saved at: `.temp_screenshots\add_attendee_20260128_151912.png`

**Analyze the screenshot to understand the UI state at failure.**

## Context Summary

Context had 13 keys: base_url, created_client_email, created_client_id, created_client_name, event_client_email, event_client_id, event_client_name, event_group_service_name, logged_in_user, password, scheduled_event_id, scheduled_event_time, username

Full context is available in the test run artifacts.

---

## Next Steps

1. Review the error message above
2. Check the screenshot to see the UI state
3. Read the test files at the location above
4. Review changelog.md for previous fixes
5. Use Playwright MCP to debug if needed

See `.cursor/rules/heal.mdc` for detailed healing process.