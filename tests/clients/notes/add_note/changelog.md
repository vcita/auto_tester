# Changelog - Add Note Test

History of fixes and changes to the Add Note test.

---

## 2026-05-26 - Stabilized Independent Notes Stress

**Error**: `ValueError: No created_matter_id in context - create_matter test must run first` when running `clients/notes` as an independent stress target.

**Root Cause**: The notes subcategory relied on the parent `clients` execution order to create a matter before note tests ran.

**Fix Applied**:
1. Added `clients/notes/_setup` to create the required matter via API for isolated subcategory runs.
2. Reused the same context keys consumed by add, edit, and delete note tests.
3. Capped touched note waits and direct navigation at 5000ms.

**Scope / Quality**: The add, edit, and delete note UI assertions remain intact; only the prerequisite matter setup was moved from parent UI dependency to API setup for independent stability validation.

---

## 2026-04-06 - Healed (Session Recovery)

**Error**: `TimeoutError: Timeout 15000ms exceeded` waiting for `#vue_wizard_iframe` to be visible.

**Root Cause**: Session was lost between `edit_contact` and `add_note`. The page redirected to the login page after clicking "Add note" (server-side 401 redirect). The wizard iframe never appeared because the page was on login, not the matter detail page.

**Fix Applied**:
1. Added `_ensure_on_matter_page` helper: checks if page is on matter URL, detects login redirect, re-logs in via `fn_login`, and navigates back to the matter page
2. Called at test start to recover before attempting any iframe interactions
3. Added post-click session check after "Add note" button click, with full retry if session was lost at that point

**Files Updated**:
- `test.py` - Added session recovery with `_ensure_on_matter_page`
- `script.md` - Updated Step 1 with session recovery documentation

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
