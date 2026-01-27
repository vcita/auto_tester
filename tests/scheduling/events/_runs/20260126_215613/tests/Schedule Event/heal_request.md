# Heal Request: scheduling/events/Events/Schedule Event

> **Generated**: 2026-01-26T21:57:58.553255
> **Test Type**: test
> **Duration**: 28202ms
**Status**: `open`

---

## What Failed

## Config

- **base_url**: `https://www.vcita.com`
- **login_url** (derived): `https://www.vcita.com/login`
- **username**: `itzik+autotest.1769433641@vcita.com`

```
Error: Locator.wait_for: Error: strict mode violation: get_by_text("Event Test Workshop 1769445591") resolved to 2 elements:
    1) <span data-v-d12fc5ae="" class="service-title">Event Test Workshop 1769445591</span> aka get_by_text("Event Test Workshop").first
    2) <span data-v-d12fc5ae="" class="service-title">Event Test Workshop 1769445591</span> aka get_by_text("Event Test Workshop").nth(1)

Call log:
  - waiting for locator("iframe[title=\"angularjs\"]").content_frame.locator("#vue_iframe_layout").content_frame.get_by_text("Event Test Workshop 1769445591") to be visible

```

**Error Type**: `Error`

## Test Location

Test files are located at: `C:\Programming\auto_tester\tests\scheduling\events\schedule_event`

- `steps.md` - Test steps and requirements
- `script.md` - Test script and flow
- `test.py` - Test implementation code
- `changelog.md` - History of previous fixes

## Screenshot

Screenshot saved at: `.temp_screenshots\schedule_event_20260126_215758.png`

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