# Heal Request: scheduling/events/Events/Cancel Event

> **Generated**: 2026-01-28T14:53:38.977394
> **Test Type**: test
> **Duration**: 5803ms
**Status**: `open`

---

## What Failed

## Config

- **base_url**: `https://www.vcita.com`
- **login_url** (derived): `https://www.vcita.com/login`
- **username**: `itzik+autotest.1769462440@vcita.com`

```
ValueError: Cancel Event control not found. Event may be in the past (completed); Cancel Event is only shown for future events. Ensure schedule_event sets a future date.
```

**Error Type**: `ValueError`

## Test Location

Test files are located at: `C:\Programming\auto_tester\tests\scheduling\events\cancel_event`

- `steps.md` - Test steps and requirements
- `script.md` - Test script and flow
- `test.py` - Test implementation code
- `changelog.md` - History of previous fixes

## Screenshot

Screenshot saved at: `.temp_screenshots\cancel_event_20260128_145337.png`

**Analyze the screenshot to understand the UI state at failure.**

## Context Summary

Context had 14 keys: base_url, created_client_email, created_client_id, created_client_name, event_attendee_id, event_client_email, event_client_id, event_client_name, event_group_service_name, logged_in_user, password, scheduled_event_id, scheduled_event_time, username

Full context is available in the test run artifacts.

---

## Next Steps

1. Review the error message above
2. Check the screenshot to see the UI state
3. Read the test files at the location above
4. Review changelog.md for previous fixes
5. Use Playwright MCP to debug if needed

See `.cursor/rules/heal.mdc` for detailed healing process.