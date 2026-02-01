# Heal Request: scheduling/appointments/Appointments/_teardown

> **Generated**: 2026-01-31T19:45:02.529875
> **Test Type**: teardown
> **Duration**: 30251ms
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
  - waiting for locator("body").get_by_text("Dashboard", exact=True)
    - locator resolved to <div data-v-50fa0c52="" data-v-23b36969="" class="VcMenuItem-text desktop VcMenuItem-userSelectNone"> Dashboard </div>
  - attempting click action
    2 × waiting for element to be visible, enabled and stable
      - element is visible, enabled and stable
      - scrolling into view if needed
      - done scrolling
      - <iframe title="angularjs" data-v-f60bb7d4="" id="angular-iframe" class="angular-iframe" data-qa="angular-iframe" data-staff-uid="gsig69hptgz2gzk0" data-business-uid="qiy4q5zf3ytv0bkv" src="https://app.vcita.com/app/dashboard?child_app=true"></iframe> from <div data-v-f60bb7d4="" data-v-58012f30="" data-v-23b36969="" class="angular-iframe is-desktop isDisplayed isFullscreen">…</div> subtree intercepts pointer events
    - retrying click action
    - waiting 20ms
    2 × waiting for element to be visible, enabled and stable
      - element is visible, enabled and stable
      - scrolling into view if needed
      - done scrolling
      - <iframe title="angularjs" data-v-f60bb7d4="" id="angular-iframe" class="angular-iframe" data-qa="angular-iframe" data-staff-uid="gsig69hptgz2gzk0" data-business-uid="qiy4q5zf3ytv0bkv" src="https://app.vcita.com/app/dashboard?child_app=true"></iframe> from <div data-v-f60bb7d4="" data-v-58012f30="" data-v-23b36969="" class="angular-iframe is-desktop isDisplayed isFullscreen">…</div> subtree intercepts pointer events
    - retrying click action
      - waiting 100ms
    56 × waiting for element to be visible, enabled and stable
       - element is visible, enabled and stable
       - scrolling into view if needed
       - done scrolling
       - <iframe title="angularjs" data-v-f60bb7d4="" id="angular-iframe" class="angular-iframe" data-qa="angular-iframe" data-staff-uid="gsig69hptgz2gzk0" data-business-uid="qiy4q5zf3ytv0bkv" src="https://app.vcita.com/app/dashboard?child_app=true"></iframe> from <div data-v-f60bb7d4="" data-v-58012f30="" data-v-23b36969="" class="angular-iframe is-desktop isDisplayed isFullscreen">…</div> subtree intercepts pointer events
     - retrying click action
       - waiting 500ms

```

**Error Type**: `TimeoutError`

## Test Location

Test files are located at: `C:\Programming\auto_tester\tests\scheduling\appointments\_teardown`

- `steps.md` - Test steps and requirements
- `script.md` - Test script and flow
- `test.py` - Test implementation code
- `changelog.md` - History of previous fixes

## Screenshot

Screenshot saved at: `.temp_screenshots\_teardown_20260131_194502.png`

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