# Heal Request: scheduling/events/Events/Schedule Event

> **Generated**: 2026-01-24T22:56:10.286576
> **Test Type**: test
> **Duration**: 12487ms
**Status**: `open`

---

## What Failed

```
TargetClosedError: Locator.press_sequentially: Target page, context or browser has been closed
Call log:
  - waiting for locator("iframe[title=\"angularjs\"]").content_frame.locator("#vue_iframe_layout").content_frame.get_by_role("textbox", name="Select service")
    - locator resolved to <input type="text" id="input-1397" autocomplete="off" islistloaded="true" placeholder="Select service" data-qa="service-select-input" customkey="common.words.custom" categoriesdata="[object Object],[object Object]"/>
  - elementHandle.type("Event Test Workshop 1769288122")

```

**Error Type**: `TargetClosedError`

## Test Location

Test files are located at: `C:\Programming\auto_tester\tests\scheduling\events\schedule_event`

- `steps.md` - Test steps and requirements
- `script.md` - Test script and flow
- `test.py` - Test implementation code
- `changelog.md` - History of previous fixes

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