# Heal Request: scheduling/appointments/Appointments/Create Appointment

> **Generated**: 2026-01-26T19:29:57.358816
> **Test Type**: test
> **Duration**: 40733ms
**Status**: `open`

---

## What Failed

## Config

- **base_url**: `https://www.vcita.com`
- **login_url** (derived): `https://www.vcita.com/login`
- **username**: `itzik+autotest.1769433641@vcita.com`

```
TimeoutError: Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for locator("iframe[title=\"angularjs\"]").content_frame.locator("#vue_iframe_layout").content_frame.get_by_role("button", name="Schedule appointment")
    - locator resolved to <button type="button" data-v-582ec022="" data-v-189b7a6a="" data-v-6e723926="" data-qa="multi-booking-modal-Schedule appointment" class="VcFooterButton v-btn v-btn--contained v-btn--is-elevated v-btn--has-bg theme--light elevation-0 v-size--default secondary VcButton primary__text">…</button>
  - attempting click action
    2 × waiting for element to be visible, enabled and stable
      - element is visible, enabled and stable
      - scrolling into view if needed
      - done scrolling
      - <div class="pac-item">…</div> from <div class="pac-container pac-logo hdpi">…</div> subtree intercepts pointer events
    - retrying click action
    - waiting 20ms
    2 × waiting for element to be visible, enabled and stable
      - element is visible, enabled and stable
      - scrolling into view if needed
      - done scrolling
      - <div class="pac-item">…</div> from <div class="pac-container pac-logo hdpi">…</div> subtree intercepts pointer events
    - retrying click action
      - waiting 100ms
    54 × waiting for element to be visible, enabled and stable
       - element is visible, enabled and stable
       - scrolling into view if needed
       - done scrolling
       - <div class="pac-item">…</div> from <div class="pac-container pac-logo hdpi">…</div> subtree intercepts pointer events
     - retrying click action
       - waiting 500ms

```

**Error Type**: `TimeoutError`

## Test Location

Test files are located at: `C:\Programming\auto_tester\tests\scheduling\appointments\create_appointment`

- `steps.md` - Test steps and requirements
- `script.md` - Test script and flow
- `test.py` - Test implementation code
- `changelog.md` - History of previous fixes

## Screenshot

Screenshot saved at: `.temp_screenshots\create_appointment_20260126_192956.png`

**Analyze the screenshot to understand the UI state at failure.**

## Context Summary

Context had 9 keys: base_url, created_client_email, created_client_id, created_client_name, created_service_id, created_service_name, logged_in_user, password, username

Full context is available in the test run artifacts.

---

## Next Steps

1. Review the error message above
2. Check the screenshot to see the UI state
3. Read the test files at the location above
4. Review changelog.md for previous fixes
5. Use Playwright MCP to debug if needed

See `.cursor/rules/heal.mdc` for detailed healing process.