# Changelog - Add Note Test

History of fixes and changes to the Add Note test.

---

## 2026-01-27 - Healed (Wizard Iframe Loading Fix)

**Error**: `TimeoutError: Locator.wait_for: Timeout 10000ms exceeded. waiting for locator("iframe[title=\"angularjs\"]").content_frame.locator("#vue_wizard_iframe").content_frame.get_by_role("button", name="Save") to be visible`

**Root Cause**: The test was trying to access the Save button inside the wizard iframe before the iframe itself was fully loaded and visible. The wizard iframe (`#vue_wizard_iframe`) appears after clicking "Add note", but needs time to load its content.

**Fix Applied**:
1. Added explicit wait for the wizard iframe locator to be visible before creating the frame_locator
2. Increased timeout for Save button wait from 10000ms to 15000ms
3. Added a brief 500ms wait after iframe appears to allow its content to load

**Changes Made**:
- Updated `test.py` Step 4 to wait for `#vue_wizard_iframe` locator before accessing frame content
- Updated `script.md` Step 4 with the new verified code pattern
- Created this changelog to document the fix

**Files Updated**:
- `test.py` - Added wizard iframe visibility wait
- `script.md` - Updated Step 4 with new code pattern
