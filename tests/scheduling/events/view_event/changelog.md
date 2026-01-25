# View Event Changelog

## 2026-01-25 - Healed (Step 2 strict mode violation on date button)
**Phase**: script.md, test.py
**Author**: Cursor AI (heal)
**Reason**: Step 2 failed — get_by_role("button", name="26") matched 4 elements
**Error**: Locator.click: strict mode violation; 4 buttons matched (January 2026, mini calendar 26, smart-scheduler 26, week range button)

**Root Cause**: The day number "26" appears in multiple places (header, mini calendar, main view, week label). Using get_by_role(..., name=str(event_day)) without scoping matched all of them.

**Fix Applied**: Scope to the mini calendar: inner_iframe.get_by_role('complementary').first.get_by_role('button', name=str(event_day)). Mini calendar is the first complementary region.

**Changes**: script.md Step 2 and test.py: use .get_by_role('complementary').first.get_by_role('button', name=str(event_day)).

**Verified Approach**: MCP run_code on Calendar page: complementary-scoped "26" button count 2 (two complementaries), nth(0).click() navigates to date.

## 2026-01-24 - Initial Build
**Phase**: All files
**Author**: Cursor AI (exploration)
**Reason**: Built from steps.md via browser exploration

**Changes**:
- Generated script.md from MCP exploration
- Generated test.py from script.md
- Opens and views event details from calendar
- Extracts scheduled_event_id from URL and saves to context
