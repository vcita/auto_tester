# Heal Request: scheduling/events/Events/Schedule Event

> **Generated**: 2026-01-26T21:47:26.217894
> **Test Type**: test
> **Duration**: 40891ms
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
  - waiting for get_by_text("Calendar", exact=True)
    - locator resolved to <div data-v-50fa0c52="" data-v-23b36969="" class="VcMenuItem-text desktop"> Calendar </div>
  - attempting click action
    2 × waiting for element to be visible, enabled and stable
      - element is visible, enabled and stable
      - scrolling into view if needed
      - done scrolling
      - <iframe title="angularjs" data-v-f60bb7d4="" id="angular-iframe" class="angular-iframe" data-qa="angular-iframe" data-staff-uid="vcu9nmpu2nf9vk14" data-business-uid="45b6258mvekdorzc" src="https://app.vcita.com/app/dashboard?child_app=true"></iframe> from <div data-v-f60bb7d4="" data-v-58012f30="" data-v-23b36969="" class="angular-iframe is-desktop isDisplayed isFullscreen">…</div> subtree intercepts pointer events
    - retrying click action
    - waiting 20ms
    2 × waiting for element to be visible, enabled and stable
      - element is visible, enabled and stable
      - scrolling into view if needed
      - done scrolling
      - <iframe title="angularjs" data-v-f60bb7d4="" id="angular-iframe" class="angular-iframe" data-qa="angular-iframe" data-staff-uid="vcu9nmpu2nf9vk14" data-business-uid="45b6258mvekdorzc" src="https://app.vcita.com/app/dashboard?child_app=true"></iframe> from <div data-v-f60bb7d4="" data-v-58012f30="" data-v-23b36969="" class="angular-iframe is-desktop isDisplayed isFullscreen">…</div> subtree intercepts pointer events
    - retrying click action
      - waiting 100ms
    53 × waiting for element to be visible, enabled and stable
       - element is visible, enabled and stable
       - scrolling into view if needed
       - done scrolling
       - <iframe title="angularjs" data-v-f60bb7d4="" id="angular-iframe" class="angular-iframe" data-qa="angular-iframe" data-staff-uid="vcu9nmpu2nf9vk14" data-business-uid="45b6258mvekdorzc" src="https://app.vcita.com/app/dashboard?child_app=true"></iframe> from <div data-v-f60bb7d4="" data-v-58012f30="" data-v-23b36969="" class="angular-iframe is-desktop isDisplayed isFullscreen">…</div> subtree intercepts pointer events
     - retrying click action
       - waiting 500ms
    - waiting for element to be visible, enabled and stable
    - element is visible, enabled and stable
    - scrolling into view if needed
    - done scrolling
    - performing click action
    - click action done
    - waiting for scheduled navigations to finish

```

**Error Type**: `TimeoutError`

## Test Location

Test files are located at: `C:\Programming\auto_tester\tests\scheduling\events\schedule_event`

- `steps.md` - Test steps and requirements
- `script.md` - Test script and flow
- `test.py` - Test implementation code
- `changelog.md` - History of previous fixes

## Screenshot

Screenshot saved at: `.temp_screenshots\schedule_event_20260126_214724.png`

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