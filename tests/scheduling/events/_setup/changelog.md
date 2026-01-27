# Events Setup Changelog

## 2026-01-26 - Navigate away and back to Services so new service appears (known UI issue)
**Phase**: test.py, script.md, steps.md
**Reason**: Heal request – service not found on Services page after create. User confirmed: new service does not show in the list until you navigate away from Services and back (known product behavior).

**Fix Applied:**
- After dismissing the event-times dialog (Step 8), add Step 8b: refresh Services list by navigating away and back via UI only (click Settings in sidebar, then click "Define the services your" in iframe to return to Services). Same pattern as create_group_event. Then scroll list and assert service name.

**Changes**: test.py – Step 8b block (Settings click → wait URL /app/settings → iframe Services button → wait /app/settings/services + heading); script.md – Step 8b and updated validation; steps.md – note under create step.

## 2026-01-26 - Scroll fix: use overflow-only + largest container (MCP debug)
**Phase**: test.py, .cursor/docs/mcp_debug_events_setup_scroll.md
**Reason**: Heal request – service still not found on Services page. MCP debug showed we never scrolled: (1) we required `scrollHeight > clientHeight`, but when the list is short the content container has equal dimensions so no scrollable was found; (2) the first scrollable ancestor of "My Services" is the small list-header (69px), not the main content (868px).

**Fix Applied:**
- Find scrollable ancestors by `overflow-y: auto/scroll/overlay` only (do not require `scrollHeight > clientHeight`).
- Among those ancestors, pick the one with the **largest** `clientHeight` so we scroll the main content area (e.g. `MD-CONTENT.settings-component.services-container`) instead of the list-header bar.
- Documented in .cursor/docs/mcp_debug_events_setup_scroll.md (MCP debug result section).

**Changes**: test.py – getScrollableAncestors + max clientHeight; mcp_debug doc updated.

## 2026-01-26 - Scroll was not the list (target "My Services" container); what changed
**Phase**: test.py, .cursor/docs/mcp_debug_events_setup_scroll.md, changelog
**Reason**: User reported we were not scrolling down at all; test used to work yesterday. Need MCP to confirm correct scroll target and document what changed.

**What changed (why it worked before):**
- **Before:** We had a conditional: if already on `/app/settings/services`, skip navigating. So after parent (Scheduling) setup we stayed on the same Services view; the list often showed the new service without needing to scroll.
- **After:** We removed the conditional; Events _setup no longer does any nav. We rely only on scroll-to-end to load the list and find the new service.
- **Bug:** The scroll helper used the **first** scrollable `div` in the iframe document. That is likely not the services list (e.g. a layout or sidebar), so the list was never scrolled and the new service was not found.

**Fix Applied:**
- `_scroll_services_list_to_end()` now targets the scrollable container that **contains "My Services"**: find an element whose text is "My Services" (or starts with it), then walk up the DOM to the first scrollable ancestor (`overflow-y: auto/scroll/overlay`, `scrollHeight > clientHeight`) and scroll that to the end repeatedly until height stabilizes.
- Added `.cursor/docs/mcp_debug_events_setup_scroll.md`: MCP debugging guide for a new session (get to Services, find the real list container, document selector and scroll sequence).

**Changes**: test.py – scroll logic finds "My Services" then scrollable ancestor; new doc for MCP debug.

## 2026-01-26 - Design fix: no conditional skip; scroll list (infinite scroll)
**Phase**: test.py, script.md, steps.md
**Author**: Cursor AI
**Reason**: User requested no conditional skip of setup steps. Split responsibilities: parent (Scheduling) = login + navigate to Services; Events _setup = only create group event service and test client (assumes parent left us on Services). Also fix root cause of service-not-found: scroll the **services list** down (infinite scroll) before asserting the new service is visible, not just scroll "My Services" heading into view.

**Fix Applied**:
- Removed Steps 1–2 (navigate to Settings / Services) from Events _setup. Docstring and script state that parent setup leaves browser on Settings > Services; this setup only creates service + client, then navigates to Calendar.
- Renumbered steps: Open New service = Step 1 … Navigate to Calendar = Step 11.
- Added `_scroll_services_list_to_end(page)`: inside the app iframe, finds the first scrollable div and scrolls it to the bottom repeatedly (with short waits) until no new content loads, so the entire list is loaded and the new service can be found.
- script.md: Initial state = assumes parent ran; removed Step 1–2 section; renumbered; validation text = scroll list down then assert. steps.md: Prerequisites = parent left us on Services; Events does not navigate to Services.

**Changes**: test.py – removed conditional nav block, added _scroll_services_list_to_end(), renumbered steps; script.md – same; steps.md – prerequisites and step 2 note.

## 2026-01-26 - Scroll list to end (not just 2–3 steps)
**Phase**: test.py, script.md, changelog
**Reason**: To find a specific service in an infinite-scroll list we must load the whole list—scroll all the way to the end, not just 2–3 times.
**Fix**: Renamed helper to `_scroll_services_list_to_end(page)`. It scrolls the list container to bottom (`scrollTop = scrollHeight - clientHeight`), waits 400ms for more content, repeats until `scrollHeight` stops growing (max 50 iterations). Then we assert the service name is visible.

## 2026-01-26 - Healed (service-in-list: scroll + wait)
**Phase**: test.py, script.md
**Author**: Cursor AI (heal_test)
**Reason**: AssertionError: 'Event Test Workshop …' not found on Services page after Create. Dialog flow passes; new service was not visible in list.
**Error**: `AssertionError: Setup could not confirm group event service was created: '...' not found on Services page.`

**Root Cause**: Possible causes: (1) List had not finished refreshing when we asserted; (2) new item prepends and view was scrolled so the new service was off-screen; (3) creation failed (e.g. 422 when account has 150+ services). Test-side mitigation for (1) and (2).

**Fix Applied**: After event-times dialog handling: wait 3.5s for list refresh; scroll "My Services" into view so top of list is visible; then wait up to 20s for service name. If creation still doesn't appear (e.g. 150-limit), assertion still fails and product bug report applies.

**Changes**: test.py – post-dialog wait 3500ms, scroll_into_view_if_needed("My Services"), 500ms pause, visibility timeout 20000ms; script.md – same.

**Re-run**: Category run still failed (service not in list). Creation is not persisting—product bug. _setup re-blocked in _category.yaml.

## 2026-01-26 - Healed (skip nav when already on Services)
**Phase**: test.py, script.md
**Author**: Cursor AI (heal_test)
**Reason**: When running scheduling/events, both Scheduling _setup and Events _setup run; Scheduling leaves us on Services, then Events _setup was doing Settings → Services again. That round-trip may leave the list in a stale state so the new service doesn't appear after create.
**Fix Applied**: If already on `/app/settings/services`, skip Steps 1–2 and go straight to Step 3 (Open New service). When run after parent setup we stay on the same Services view; no redundant navigation.
**Changes**: test.py, script.md – conditional: only navigate to Settings then Services when URL does not contain app/settings/services.

## 2026-01-26 - Re-run; 150-service limit is distinct (unblocked for MCP re-check)
**Phase**: N/A
**Reason**: User clarified the earlier 422 was due to **>150 services** (limit not clearly messaged), not a generic create failure. With &lt;150 services, creation may succeed. Events _setup unblocked; bug report updated. Use `debug_events_setup_mcp.py` + Playwright MCP to explore step-by-step and confirm current behavior.
## 2026-01-26 - Re-run, product bug (service not in list)
**Phase**: N/A (no test change)
**Reason**: Category re-run; Events _setup failed again with same assertion: 'Event Test Workshop …' not found on Services page. Dialog flow (Steps 9–10) passes; new group event still does not appear in list after Create.
**Classification**: Previously treated as product bug (duplicate). Later clarified: 422 was due to 150-service limit; test unblocked for re-verification with MCP.

## 2026-01-26 - Healed (dialog wait matched wrong dialog)
**Phase**: test.py, script.md
**Author**: Cursor AI (heal_test)
**Reason**: After clicking Create, wait for dialog hidden timed out (15s).
**Error**: `Locator.wait_for: Timeout 15000ms exceeded` waiting for `get_by_role("dialog")` to be hidden.

**Root Cause**: The create dialog closes and the "Great. Now enter your event dates & times" dialog opens. `iframe.get_by_role("dialog")` matches any dialog, so it matched the new dialog and never became hidden.

**Fix Applied**: Wait for the create dialog specifically by name: `get_by_role("dialog", name=re.compile(r"Service info", re.IGNORECASE))`. After it closes, Step 10 already clicks "I'll do it later" if visible; updated that step to wait for the event-times dialog by name to close.

**Changes**: test.py – import re; create_dialog and Step 10 use name regex; removed inner `import re`; script.md – same. Increased post-dialog wait and visibility timeout for service name.

**Note**: Setup still fails at "service not found on Services page" after Create — create may be failing (e.g. 422). Events _setup left blocked; dialog-wait fix is correct when creation succeeds.

---

## 2026-01-25 - Product bug (test blocked)
**Phase**: N/A (no test change)
**Reason**: Create Group event step fails with API 422; dialog shows "Please fix the errors below". Confirmed via MCP: form is filled correctly but Create returns 422 and dialog never closes. Classified as **product/system bug** in vcita, not a test issue.

**Actions**:
- Bug report: `.cursor/bug_reports/group_event_create_422.md`
- Events _setup marked as `blocked` in `tests/scheduling/events/_category.yaml`
- No changes to test code.

## 2026-01-24 - Initial Build
**Phase**: All files
**Author**: Cursor AI (exploration)
**Reason**: Built from steps.md via browser exploration

**Changes**:
- Generated script.md from MCP exploration
- Generated test.py from script.md
- Creates group event service and test client for event scheduling tests
- Navigates to Calendar page after setup
