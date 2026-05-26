# Changelog

## 2026-05-26 - Stabilize Clients Page Readiness
**Phase**: Test
**Author**: Cursor AI
**Reason**: 10-run stress validation showed intermittent clients-page navigation/loading timeouts before opening the Status filter.
**Changes**:
- Navigate directly to the Clients route instead of relying on sidebar navigation from settings.
- Wait for Clients page readiness before opening filters.
- Retry the Status filter dropdown when the filter options render slowly.
- Retry the Client Card settings page when it remains on the initial loader.
- Reapply the Status filter when the Clients table remains stuck on its blocking loader.

## 2026-05-25 - Fresh Validation Passed
**Phase**: Validation
**Author**: Cursor AI
**Reason**: Backfilled the migration tracker with fresh original-vs-migrated evidence.
**Changes**:
- Original automation-js feature passed with 2 scenarios and 20 steps in 1m47.029s.
- Migrated custom_status scope passed with 2/2 tests in 73.6 seconds.
- Final stress validation passed 3/3 iterations after filter popover retry stabilization.

## 2026-05-25 - Retry Opening Status Filter
**Phase**: Test
**Author**: Cursor AI
**Reason**: Stress validation captured the clients table loaded with both expected clients, but the filter popover was closed while waiting for the Status filter option.
**Changes**:
- Retry opening the Filters popover once before failing on a missing Status filter control.

## 2026-05-25 - Extend Clients Table Readiness Wait
**Phase**: Test
**Author**: Cursor AI
**Reason**: Stress validation showed the Clients page can stay on the loading spinner for more than the generic 5 second UI timeout after returning from a client detail page.
**Changes**:
- Added a dedicated 45 second timeout for waiting on the CRM table filter toolbar.
- Kept the existing dynamic filtered-client assertion for actual data indexing.

## 2026-05-25 - Use Current Client Header Edit Selector
**Phase**: Test
**Author**: Cursor AI
**Reason**: Fresh headed validation reached the client page but timed out waiting for the legacy contact details edit button.
**Changes**:
- Reused the current client-card edit selector from the edit contact test.
- Wait for the Angular iframe and edit contact dialog before changing the status.

## 2026-05-24 - Stabilize Second Client Status
**Phase**: Steps, script, test
**Author**: Cursor AI
**Reason**: Repeated focused runs showed the `status` field on API client creation is not consistently reflected in CRM filtering.
**Changes**:
- Keep creating the second client through the API with the custom status payload.
- Open the API-created second client and ensure the status is present via the same UI path before asserting the two-client filter result.

## 2026-05-24 - Extend CRM Index Wait
**Phase**: Test
**Author**: Cursor AI
**Reason**: API-created clients can lag behind CRM table indexing; the second API-created client was not visible within the first 60 seconds.
**Changes**:
- Extended the dynamic filtered-client condition wait to 150 seconds.

## 2026-05-24 - Scope CRM Filter Readiness
**Phase**: Test
**Author**: Cursor AI
**Reason**: Focused run found `get_by_role("button", name="Filters")` also matched the active filter summary button.
**Changes**:
- Wait for the CRM table filter action via `.table-actions__filter` instead of the ambiguous button role.

## 2026-05-24 - Open API Client By ID For Status Assignment
**Phase**: Test
**Author**: Cursor AI
**Reason**: The CRM table intentionally remained empty under the custom status filter, so searching from that state could not open the API-created client.
**Changes**:
- Open the API-created client detail page by returned client ID before assigning the custom status.

## 2026-05-24 - Stabilize Settings To Clients Navigation
**Phase**: Test
**Author**: Cursor AI
**Reason**: Focused run left the Clients page on a spinner after clicking from Client Card settings, so the Filters toolbar never rendered.
**Changes**:
- Navigate directly to the app Clients route from settings before waiting for the CRM toolbar.

## 2026-05-24 - Clear Status Filter Before Client Search
**Phase**: Test
**Author**: Cursor AI
**Reason**: Focused run timed out opening the API-created client because the Status filter remained active after the empty-filter assertion.
**Changes**:
- Switched filter clearing to click the visible `Clear all` action and wait for it to disappear before searching the client list.

## 2026-05-24 - Fix Status Input Strict Mode
**Phase**: Test
**Author**: Cursor AI
**Reason**: Focused run found `div.client-custom-statuses input` matched both the visible text input and a hidden combobox input.
**Changes**:
- Switched custom status creation to the visible `Add statuses` placeholder locator.

## 2026-05-24 - Initial Migration
**Phase**: Steps, script, test
**Author**: Cursor AI
**Reason**: Migrated automation-js custom status create/filter scenario into auto_tester.
**Changes**:
- Added Phase 1 steps covering custom status creation, assignment, and CRM filtering.
- Added Phase 2 script mapping legacy Selenium page-object behavior to Playwright actions.
- Added Phase 3 test using API client setup and UI validation for status assignment/filtering.
