# Changelog - Create Custom Appointment

## 2026-01-26 - Healed (Required Address field)

**Phase**: script.md, test.py
**Author**: Cursor AI (heal)
**Reason**: Test failed at Step 11 (verify appointment in calendar) because appointment was never created
**Error**: `TimeoutError: Locator.wait_for: Timeout 15000ms exceeded` waiting for `menuitem` with custom title

**Root Cause**: The "New Appointment" modal now has a required "Address" field. The test selected "My business address" for Location but did not fill the separate "Address" input. Form validation kept the modal open and blocked scheduling, so the appointment never appeared in the calendar.

**Fix Applied**: Added Step 9b: fill the "Address" textbox with "My business address" after selecting location and before clicking "Schedule appointment".

**Changes**:
- script.md: Added Step 9b with VERIFIED PLAYWRIGHT CODE; aligned Step 9 location dropdown with test.py (regex for arrow_drop_down).
- test.py: Inserted Step 9b to locate and fill `inner_iframe.get_by_role('textbox', name='Address')`.

**Verified Approach**: Based on failure screenshot showing modal with empty "Address" and "Required field" message; fix addresses the validation barrier. (MCP validation recommended when available.)
