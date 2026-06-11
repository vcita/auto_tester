# Cancel Event Changelog

## 2026-01-25 - Healed (Step 5: Event List sidebar item hidden when submenu collapsed)
**Phase**: test.py
**Author**: Cursor AI (heal)
**Reason**: Step 5 failed — timeout waiting for Event List sidebar item to be visible
**Error**: `TimeoutError: Locator.wait_for: Timeout 10000ms exceeded` on `[data-qa="VcMenuItem-calendar-subitem-event_list"]` to be visible; call log showed locator resolved to **hidden** (23×).

**Root Cause**: After clicking Calendar, the Event List sub-item can remain hidden when the Calendar submenu is collapsed (element is in DOM but not visible). We had switched to `wait_for(state='visible')` which never passes in that UI state.

**Fix Applied**: Use `wait_for(state='attached', timeout=10000)` for the Event List sidebar item in both places (Step 2a and Step 5), then force click with evaluate. Same pattern as previous heal; restores attached + force click instead of visible.

**Changes**: test.py Step 2a and Step 5 – event_list_item.wait_for(state='attached') and force click; added HEALED comments.

## 2026-01-25 - Healed (Step 5: Event List nav + row locator)
**Phase**: script.md, test.py
**Author**: Cursor AI (heal)
**Reason**: Step 5 failed — Event List sidebar item "element is not visible" when verifying CANCELLED
**Error**: Locator.click timeout on [data-qa="VcMenuItem-calendar-subitem-event_list"].first; element not visible

**Root Cause**: After navigating to calendar, Calendar submenu was collapsed so Event List item was not visible; wait was 1000ms and normal click failed. Also event row used [cursor="pointer"] which is not an HTML attribute.

**Fix Applied**: 1) Wait 1500ms after clicking Calendar; wait_for(state='attached') on Event List item; use evaluate('el => el.click()') to force click. 2) Use inner_iframe.get_by_text(service_name) instead of locator('[cursor="pointer"]').filter(has_text=...). 3) Get row text via event_cell.first.evaluate(closest list-item/row) so "CANCELLED" (sibling in row) is included; added 2s wait before opening Event List so cancellation propagates.

## 2026-01-24 - Initial Build
**Phase**: All files
**Author**: Cursor AI (exploration)
**Reason**: Built from steps.md via browser exploration

**Changes**:
- Generated script.md from MCP exploration
- Generated test.py from script.md
- Cancels the scheduled event with optional cancellation message
- Clears event context variables after cancellation
- Navigates to calendar page after cancellation
