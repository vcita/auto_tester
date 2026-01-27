# Schedule Event Changelog

## 2026-01-26 - Prefer _setup service name in dropdown (fix View Event wrong event)
**Phase**: test.py
**Reason**: View Event was looking for "Event Test Workshop 1769445591" (wrong) instead of the service just created in _setup ("Event Test Workshop 1769458997"). schedule_event was using .first "Event Test Workshop" and overwriting context with that option's name, so the newly created service was ignored.

**Fix Applied**: Prefer the option that matches context["event_group_service_name"] (from _setup). If that option is visible in the listbox within 5s, select it and keep context. Otherwise fall back to first "Event Test Workshop", parse its name, and update context as before.

**Changes**: test.py Step 4: try option.filter(has_text=expected_name).first; on success use expected_name; else fall back to first "Event Test Workshop" and set context.

## 2026-01-25 - Healed (Step 4 service combobox option timeout)
**Phase**: script.md, test.py
**Author**: Cursor AI (heal)
**Reason**: Schedule Event failed waiting for service option to be visible after typing in combobox
**Error**: `TimeoutError: Locator.wait_for: Timeout 10000ms exceeded` on `get_by_role("option").filter(has_text="Event Test Workshop ...").first` to be visible

**Root Cause**: MCP showed listbox and role="option" elements exist and filter works. The timeout was likely due to (1) async filter re-render after typing, or (2) API lag when the service was just created in _setup. No selector bug; need to re-assert listbox after typing and allow longer for the option to appear.

**Fix Applied**: After press_sequentially, re-assert listbox visible (handles re-render); increase option wait timeout from 10s to 15s; select the filtered option directly (all_options.first.click()) instead of re-querying all options and looping.

**Changes**:
- test.py Step 4: listbox.wait_for(state='visible', timeout=5000) after typing; all_options.first.wait_for(state='visible', timeout=15000); use all_options.first for click, remove loop.
- script.md Step 4: same VERIFIED PLAYWRIGHT CODE updates; HEALED note.

**Verified Approach**: MCP: opened Calendar, New → Group event, clicked combobox; listbox showed options with role=option. Typed "Event Test Workshop"; get_by_role('option').filter(hasText: ...).count() === 19, first visible. Fix adds listbox re-wait and 15s timeout.

## 2026-01-25 - Healed (Step 5 date picker menu locator)
**Phase**: script.md, test.py
**Author**: Cursor AI (heal)
**Reason**: Schedule Event failed waiting for date picker menu to be hidden after selecting day
**Error**: `TimeoutError: Locator.wait_for: Timeout 5000ms exceeded` on `get_by_role("menu").first.wait_for(state='hidden')`

**Root Cause**: `get_by_role('menu')` in the iframe matches the scheduler's events container (`<div role="menu" smart-id="allDayEventsContainer" class="smart-scheduler-events-container">`) first. That element stays visible; the date picker is a different menu. Waiting for `.first` to be hidden meant waiting for the wrong element.

**Fix Applied**: Stop using generic menu locator. Wait for date picker to open by waiting for tomorrow's day button to be visible; after clicking the day, wait for that same day button to become hidden (picker closed).

**Changes**:
- test.py Step 5: wait for `tomorrow_date_btn.first.wait_for(state='visible')` then `day_btn.click()` then `day_btn.wait_for(state='hidden')`; removed date_picker_menu.
- script.md Step 5: VERIFIED PLAYWRIGHT CODE updated to same pattern; added HEALED note.

**Verified Approach**: Root cause from heal request call log (locator resolved to allDayEventsContainer). Fix avoids any role=menu for this step.

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
