# Heal Request: scheduling/appointments/Appointments/Reschedule Appointment

> **Generated**: 2026-01-31T19:44:31.893608
> **Test Type**: test
> **Duration**: 39646ms
**Status**: `open`

---

## What Failed

## Config

- **base_url**: `https://www.vcita.com`
- **login_url** (derived): `https://www.vcita.com/login`
- **username**: `itzik+autotest.1769462440@vcita.com`

```
TimeoutError: Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for locator("iframe[title=\"angularjs\"]").content_frame.get_by_text("10:00am", exact=True)
    - locator resolved to <li tabindex="-1" role="option" class="k-item" unselectable="on">10:00am</li>
  - attempting click action
    2 × waiting for element to be visible, enabled and stable
      - element is not visible
    - retrying click action
    - waiting 20ms
    2 × waiting for element to be visible, enabled and stable
      - element is not visible
    - retrying click action
      - waiting 100ms
    57 × waiting for element to be visible, enabled and stable
       - element is not visible
     - retrying click action
       - waiting 500ms

```

**Error Type**: `TimeoutError`

## Test Location

Test files are located at: `C:\Programming\auto_tester\tests\scheduling\appointments\reschedule_appointment`

- `steps.md` - Test steps and requirements
- `script.md` - Test script and flow
- `test.py` - Test implementation code
- `changelog.md` - History of previous fixes

## Screenshot

Screenshot saved at: `.temp_screenshots\reschedule_appointment_20260131_194431.png`

**Analyze the screenshot to understand the UI state at failure.**

## Context Summary

Context had 12 keys: base_url, created_appointment_client, created_appointment_service, created_client_email, created_client_id, created_client_name, created_service_id, created_service_name, last_appointment_note, logged_in_user, password, username

Full context is available in the test run artifacts.

---

## Next Steps

1. Review the error message above
2. Check the screenshot to see the UI state
3. Read the test files at the location above
4. Review changelog.md for previous fixes
5. Use Playwright MCP to debug if needed

See `.cursor/rules/heal.mdc` for detailed healing process.