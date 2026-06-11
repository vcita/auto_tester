# Changelog

## 2026-06-02 - Wait for clients widget to settle before reading (VCITA2-13787)
**Phase**: Test
**Author**: Cursor AI (stabilization)
**Reason**: In a full-suite headless run the test failed at Step 5 with `AssertionError: Expected recently active clients ['first last'], got []`. The failure screenshot showed the client ("first last", "Last activity: Jun 02") **rendered in the widget** — so the data was present. Root cause: after each dashboard reload the clients widget loads its rows asynchronously (renders `VcSkeleton` first), and the helper read `[data-qa="VcClientItem"]` before that load settled, getting an empty list.
**Changes**:
- Added `_wait_for_clients_widget_loaded()`: event-based wait (capped at the 5s `UI_TIMEOUT`) until the widget settles — no `VcSkeleton` present AND a `VcClientItem` row or `VcEmptyState` rendered — before reading rows.
- Replaced the time-based propagation poll with a bounded `WIDGET_RELOAD_ATTEMPTS = 3` reload loop. No fixed sleeps and no wait exceeds the 5s cap; each reload itself gives the search index a moment to propagate, and the loop returns as soon as the expected clients appear.
- Assertion unchanged: still asserts exact expected names and order, still fails with a clear, data-driven message.
**Validation**: Re-ran `clients/recently_active` headless x3; passed each time.

## 2026-05-26 - Retry Dashboard Widget Readiness
**Phase**: Test
**Author**: Cursor AI
**Reason**: 10-run stress validation had one timeout while the dashboard clients widget was still not ready after appointment creation.
**Changes**:
- Retry transient Playwright readiness timeouts inside the recently-active indexing window.
- Keep the assertion data-driven instead of adding a fixed sleep.

## 2026-05-24 - Cache Staff Lookup
**Phase**: Test
**Author**: Cursor AI
**Reason**: Runtime review found the helper fetched the first staff UID once for service creation and again for each appointment.
**Changes**:
- Cache `recently_active_staff_uid` in context after the first staff lookup.
- Reuse the cached staff UID for both appointment API calls.

## 2026-05-24 - Validation Passed
**Phase**: Validation
**Author**: Cursor AI
**Reason**: Confirmed migrated coverage works on integration and preserves the original scenario behavior.
**Changes**:
- Focused migrated run passed with 1/1 tests in 25.2 seconds.
- Stress test passed 3/3 iterations with fresh auto-created accounts.
- Original automation-js feature passed with 1/1 scenarios and 11/11 steps in 24.224 seconds.

## 2026-05-24 - Parse POV Client Item Names
**Phase**: Test
**Author**: Cursor AI
**Reason**: Focused validation showed `VcClientItem` text starts with avatar initials before the client name.
**Changes**:
- Ignore short uppercase avatar-initial lines when reading client names from the dashboard widget.

## 2026-05-24 - Support Current Dashboard Widget
**Phase**: Script, test
**Author**: Cursor AI
**Reason**: Focused validation showed integration renders the POV dashboard rather than the legacy Angular dashboard expected by the original feature flag setup.
**Changes**:
- Select the Clients widget's recently active view through the widget's saved view localStorage key.
- Assert the current dashboard with stable `data-qa` selectors for empty state and client items.
- Keep the legacy `.dashboard-clients-container` assertion path as a fallback.

## 2026-05-24 - Initial Migration
**Phase**: Steps, script, test
**Author**: Cursor AI
**Reason**: Migrated automation-js recently active clients dashboard scenario into auto_tester.
**Changes**:
- Added Phase 1 steps covering empty, one-client, and two-client dashboard states.
- Added Phase 2 script mapping legacy API setup and dashboard assertions to Playwright.
- Added Phase 3 test using API-created service, clients, and appointments.
- Added local helpers for account API requests and legacy dashboard widget assertions.
- Preserved seeker-indexing behavior with a bounded polling loop and dashboard reloads.
