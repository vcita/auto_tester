# Delete Service Function - Changelog

## 2026-05-27 - Restored UI Deletion Scope

**Phase**: test.py, script.md
**Author**: Cursor AI (scope correction)
**Reason**: API-based teardown skipped Settings navigation, Services list selection, Delete action, confirmation, and removal verification, reducing the UI E2E scope this function is meant to cover.

**Fix Applied**:
1. Removed the `created_service_id` API deletion shortcut.
2. Removed API helper code and token/base URL handling from the UI function.
3. Restored the full Settings → Services → service row → Delete → Ok → list verification flow for all callers.

**Scope / Quality**: `created_service_id` may still be cleared after deletion, but it no longer changes the deletion path. The function now validates the UI deletion behavior every time.

---

## 2026-05-27 - Stabilized ID-Based Service Teardown

**Phase**: test.py, script.md
**Author**: Cursor AI (stabilization)
**Reason**: `scheduling/appointments` 10-iteration stress failed in teardown while navigating Settings → Services; screenshot showed the Settings loader still spinning.

**Root Cause**: Service teardown depended on the Settings landing page, service editor toolbar, and virtualized Services list even when the created service ID was already known.

**Fix Applied**:
1. If `created_service_id` exists, delete via the same backend route used by Restangular: `DELETE /v2/settings/services/{id}`.
2. Keep the old UI path only as a fallback for callers without a service ID.
3. Cap touched API/UI waits/navigation at 5000ms.

**Scope / Quality**: This is teardown cleanup, not the service deletion behavior test. The dedicated scheduling/services delete flow still covers UI deletion; teardown now removes generated setup data by ID without weakening appointment assertions.

---

## 2026-01-31 - Healed (Services list endless scroll — scroll to find service before click)

**Phase**: test.py, script.md
**Author**: Cursor AI (heal_test, screenshot + MCP)
**Reason**: Appointments teardown Step 2 failed: TimeoutError waiting for `iframe.get_by_role("button").filter(has_text="Appointment Test Service 1769890569")` to be visible. Failure screenshot showed Settings / Services page with "Event Test Workshop" services visible; the appointment test service was not in the initial view.

**Root Cause**:
The Services list uses endless/virtual scroll. The service to delete ("Appointment Test Service ...") is often below the fold. fn_delete_service did not scroll the list, so the service button never became visible within 10s.

**Fix Applied**:
Add scroll-to-find logic (same pattern as tests/scheduling/services/delete_service/test.py): (1) Wait for "My Services" to confirm list loaded. (2) Scroll loop (up to 10 times): check if service button is present; if not, find last visible test service (regex) and scroll it into view, or scroll "Add 1 on 1 Appointment" into view; brief settle. (3) Then wait for service button visible (30s) and click.

**Changes**:
- test.py: Added `import re`. After Step 2b, wait for "My Services", then scroll loop; increased service_in_list wait to 30000ms.
- script.md: Step 3 LOCATOR DECISION and VERIFIED PLAYWRIGHT CODE updated with scroll logic.

**Verified Approach**: MCP showed Services list with many items; delete_service category test already uses this scroll pattern. Same logic applied to fn_delete_service.

---

## 2026-01-31 - Healed (Settings navigation timeout in teardown)

**Phase**: test.py, script.md
**Author**: Cursor AI (heal_test)
**Reason**: Appointments teardown failed with "Could not delete service: Locator.click: Timeout 30000ms exceeded - waiting for get_by_text('Settings')".

**Root Cause**: When teardown runs after calendar tests, the browser is on the calendar page. The function called `page.get_by_text('Settings').click()` with no prior wait. The Settings link in the sidebar may not be visible/ready immediately (e.g. main page vs iframe focus, or sidebar not yet painted), so the click timed out.

**Fix Applied**: Wait for page and sidebar before Settings: `wait_for_load_state("domcontentloaded")`, wait for sidebar item "Calendar" (attached, 30s) since we're on calendar, brief settle, then find Settings (attached, 15s), scroll_into_view_if_needed(), click(force=True), wait_for_url 30s. Uses .first to take sidebar match; force click when element may not be strictly visible.

**Changes**: test.py – Step 1 now waits for Settings visible and scrolls into view before click; script.md – Step 1 updated with same VERIFIED PLAYWRIGHT CODE.

**Verified Approach**: Pattern already used in create_service (navigate to Settings from dashboard) and events _teardown (Settings fallback); aligns with project wait strategy (event-based, long timeout).

---

## 2026-01-23 - Initial Build

**Phase**: All files
**Author**: Cursor AI (exploration)
**Reason**: Built from steps.md via browser exploration with Playwright MCP

**Changes**:
- Created steps.md defining service deletion flow
- Generated script.md from MCP exploration with verified locators
- Generated test.py from script.md

**Verified Locators**:
- Settings navigation: `page.get_by_text('Settings')`
- Services button: `iframe.get_by_role('button', name='Define the services your')`
- Service in list: `iframe.get_by_role('button').filter(has_text=name)`
- Delete button: `iframe.get_by_role('button', name='Delete')`
- Ok confirmation: `iframe.get_by_role('button', name='Ok')`

**Notes**:
- Function can accept name parameter or read from context
- Clears `created_service_id` and `created_service_name` from context after deletion
- Includes verification that service no longer appears in list
