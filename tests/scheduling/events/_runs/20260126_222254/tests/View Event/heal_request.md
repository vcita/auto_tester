# Heal Request: scheduling/events/Events/View Event

> **Generated**: 2026-01-26T22:24:09.951949
> **Test Type**: test
> **Duration**: 1669ms
**Status**: `open`

---

## What Failed

## Config

- **base_url**: `https://www.vcita.com`
- **login_url** (derived): `https://www.vcita.com/login`
- **username**: `itzik+autotest.1769433641@vcita.com`

```
Error: Locator.wait_for: Error: strict mode violation: get_by_role("menuitem").filter(has_text="Event Test Workshop 1769445591") resolved to 3 elements:
    1) <div tabindex="0" role="menuitem" aria-haspopup="true" id="1p89l7slary8rd8e" staff_uid="vcu9nmpu2nf9vk14" class="smart-scheduler-event" title="0/10↵Event Test Workshop 1769445591↵03:00 PM - 04:00 PM↵1a11">…</div> aka get_by_role("button").filter(has_text="today 25-31 January 2026 week")
    2) <div tabindex="0" role="menuitem" aria-haspopup="true" id="euauwz64a3yb0dto" staff_uid="vcu9nmpu2nf9vk14" class="smart-scheduler-event" title="0/10↵Event Test Workshop 1769445591↵03:00 PM - 04:00 PM↵dfgdfgdfg">…</div> aka get_by_role("button").filter(has_text="today 25-31 January 2026 week")
    3) <div tabindex="0" role="menuitem" aria-haspopup="true" id="32t1di25k2d6t01r" staff_uid="vcu9nmpu2nf9vk14" class="smart-scheduler-event" title="0/10↵Event Test Workshop 1769445591↵04:00 PM - 05:00 PM↵gfdgdg">…</div> aka get_by_role("button").filter(has_text="today 25-31 January 2026 week")

Call log:
  - waiting for locator("iframe[title=\"angularjs\"]").content_frame.locator("#vue_iframe_layout").content_frame.get_by_role("menuitem").filter(has_text="Event Test Workshop 1769445591") to be visible

```

**Error Type**: `Error`

## Test Location

Test files are located at: `C:\Programming\auto_tester\tests\scheduling\events\view_event`

- `steps.md` - Test steps and requirements
- `script.md` - Test script and flow
- `test.py` - Test implementation code
- `changelog.md` - History of previous fixes

## Screenshot

Screenshot saved at: `.temp_screenshots\view_event_20260126_222409.png`

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