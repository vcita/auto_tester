# Schedule Event Changelog

## 2026-01-25 - Healed (Step 9 outcome verification selector)
**Phase**: script.md, test.py
**Author**: Cursor AI (heal)
**Reason**: Step 9 failed — timeout waiting for event row in Event List
**Error**: `TimeoutError: Locator.wait_for: Timeout 10000ms exceeded` on `locator("[cursor=\"pointer\"]").filter(has_text="...")`

**Root Cause**: The selector `[cursor="pointer"]` targets an HTML attribute that does not exist. In the DOM, cursor is a CSS property (style), not an attribute. Playwright's accessibility tree shows `[cursor=pointer]` but the actual elements have no `cursor` attribute, so the locator matched 0 elements (verified in MCP with run_code: byAttrCount=0, byTextCount=1).

**Fix Applied**: Replaced event row locator with `inner_iframe.get_by_text(service_name)` and wait for visible. Same flow (navigate to Event List, search by event name, assert event visible, return to Calendar).

**Changes**:
- script.md Step 9: use `get_by_text(service_name)` and `event_cell.wait_for(state='visible')` instead of `locator('[cursor="pointer"]').filter(has_text=...)`.
- test.py Step 9: same change; added HEALED comment.

**Verified Approach**: MCP run_code on Event List page: `locator('[cursor="pointer"]').filter(hasText: name).count() === 0`, `getByText(name).count() === 1`, `getByText(name).waitFor({ state: 'visible' })` succeeded.

## 2026-01-24 - Initial Build
**Phase**: All files
**Author**: Cursor AI (exploration)
**Reason**: Built from steps.md via browser exploration

**Changes**:
- Generated script.md from MCP exploration
- Generated test.py from script.md
- Schedules a group event instance by selecting service, date, and time
- Saves scheduled_event_time to context
