# Appointments Teardown - Changelog

## 2026-01-31 - Healed (Teardown failed: searchbox timeout in fn_delete_client)

**Phase**: Fix in tests/_functions/delete_client (shared function used by teardown)
**Author**: Cursor AI (heal)
**Reason**: Teardown failed with TimeoutError waiting for searchbox "Search by name, email, or phone number" when deleting the test client.

**Root Cause**:
fn_delete_client navigates to the clients/properties list and looks for the list filter searchbox by name. On the Properties page the list searchbox has no (or different) accessible name; the test locator never matched. Failure occurred at fn_delete_client Step 2 (search field).

**Fix Applied**:
Fixed in delete_client function (not in _teardown code): wait for list toolbar (Filters button), then use the second searchbox (list filter) via `page.get_by_role("searchbox").nth(1)`. See tests/_functions/delete_client/changelog.md 2026-01-31.

**Result**: ✅ Teardown can complete client deletion; no changes needed in _teardown test.py itself.

---

## 2026-01-31 - Healed (Step 0: fullscreen iframe intercepts Dashboard click)

**Phase**: test.py, script.md
**Author**: Cursor AI (heal)
**Reason**: Teardown failed when not on dashboard: click on "Dashboard" timed out — "iframe ... subtree intercepts pointer events" (fullscreen angular-iframe covering sidebar after e.g. Reschedule failure).

**Root Cause**:
When a test (e.g. Reschedule Appointment) fails, the app can be left with a fullscreen iframe (calendar/reschedule UI) covering the main page. Teardown Step 0 finds "Dashboard" but the click is intercepted by the iframe.

**Fix Applied**:
Before clicking Dashboard, press Escape 3 times with short delays to dismiss any modal/overlay, then wait 500ms, then click Dashboard as before.

**Changes**:
- test.py Step 0: Add keyboard.press("Escape") x3 + short waits before locating and clicking Dashboard.
- script.md Step 0: Document Escape and reason.

**Result**: ✅ Teardown can reach Dashboard when iframe was covering sidebar.

---

## 2026-01-31 - Delete option in fn_delete_client (HEALED)

Delete option on client detail page: use `iframe.get_by_text("Delete").first` (options are not role=menuitem; menu container may not have role=menu). Fixed in tests/_functions/delete_client; client deletion in teardown now completes. Service deletion (fn_delete_service) may still fail on service list locator — separate heal if needed.
