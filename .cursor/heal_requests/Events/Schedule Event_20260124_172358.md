# Heal Request: scheduling/events/Events/Schedule Event

> **Generated**: 2026-01-24T17:23:58.428430
> **Test Type**: test
> **Duration**: 16356ms
**Status**: `open`

---

## What Failed

```
Error: Locator.text_content: Error: strict mode violation: get_by_role("button", name="End Date:") resolved to 2 elements:
    1) <div role="button" label="End Date:" data-v-66df3d06="" autocomplete="off" aria-haspopup="true" aria-expanded="false" color="rgba(0, 0, 0, 0.4)" clear-icon="far fa-times-circle" prepend-inner-icon="icon-Calendar" class="v-input vcita-text-input date-picker-text-input v-input--hide-details v-input--is-label-active v-input--is-dirty v-input--is-readonly theme--light v-text-field v-text-field--is-booted">…</div> aka get_by_role("button", name="End Date:").first
    2) <input type="" step="1" role="button" id="input-822" autocomplete="off" readonly="readonly" aria-haspopup="true" aria-expanded="false" data-qa="date-picker-text-input"/> aka get_by_label("End Date:")

Call log:
  - waiting for locator("iframe[title=\"angularjs\"]").content_frame.locator("#vue_iframe_layout").content_frame.get_by_role("button", name="End Date:")

```

**Error Type**: `Error`

## Test Location

Test files are located at: `C:\Programming\auto_tester\tests\scheduling\events\schedule_event`

- `steps.md` - Test steps and requirements
- `script.md` - Test script and flow
- `test.py` - Test implementation code
- `changelog.md` - History of previous fixes

## Screenshot

Screenshot saved at: `.temp_screenshots\schedule_event_20260124_172358.png`

**Analyze the screenshot to understand the UI state at failure.**

## Context Summary

Context had 9 keys: created_client_email, created_client_id, created_client_name, event_client_email, event_client_id, event_client_name, event_group_service_name, logged_in_user, scheduled_event_time

Full context is available in the test run artifacts.

---

## Next Steps

1. Review the error message above
2. Check the screenshot to see the UI state
3. Read the test files at the location above
4. Review changelog.md for previous fixes
5. Use Playwright MCP to debug if needed

See `.cursor/rules/heal.mdc` for detailed healing process.