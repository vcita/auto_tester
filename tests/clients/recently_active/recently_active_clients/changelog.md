# Changelog

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
