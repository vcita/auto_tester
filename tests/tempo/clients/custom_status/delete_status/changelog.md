# Changelog

## 2026-05-27 - Stabilize Status Reassignment
**Phase**: Test
**Author**: Cursor AI
**Reason**: Full `clients` stress showed the shared status reassignment helper could miss the current client-detail frame or the rendered Status dropdown.
**Changes**:
- Reuse the hardened client-detail readiness and contact edit dialog opening path.
- Select the visible Angular Material Status dropdown/options before saving the reassignment to `Lead`.
- Keep the source-of-truth assertions that deletion is blocked while in use and succeeds after reassignment.

## 2026-05-26 - Retry Client Card Settings Readiness
**Phase**: Test
**Author**: Cursor AI
**Reason**: Stress validation showed the Client Card settings page can stay on the full-page loader before status deletion.
**Changes**:
- Retry opening Client Card settings until the Client status tab and status input are ready.
- Keep the delete flow waiting on UI state instead of adding a fixed sleep.
- Removed redundant CRM filter-list checks from the delete scenario; Client Card settings remains the source-of-truth for blocked and completed deletion.

## 2026-05-24 - Dismiss In-Use Status Dialog Explicitly
**Phase**: Test
**Author**: Cursor AI
**Reason**: Headless validation showed the in-use delete blocker appears as a "Cannot delete status" dialog that the generic role dialog detector did not catch.
**Changes**:
- Detect the "Cannot delete status" blocker by title.
- Click the first actually visible `Ok` action and wait for the dialog to close before asserting the status remains available.
- Check the nested Vuetage iframe where the Client Card status dialog is rendered in headless runs.

## 2026-05-24 - Restore Deleted Status Filter Assertion
**Phase**: Steps, script, test
**Author**: Cursor AI
**Reason**: Code review found scope loss because the migrated delete flow stopped verifying that the deleted status disappears from CRM Status filter options.
**Changes**:
- Restored the deleted-status filter option assertion after unused status deletion.
- Switched CRM list navigation to visible sidebar navigation through Dashboard before opening filters.

## 2026-05-24 - Verify Deletion In Client Card Settings
**Phase**: Steps, script, test
**Author**: Cursor AI
**Reason**: The original legacy delete scenario validates removal from Client Card settings; navigating back to CRM after deletion intermittently left the Clients page on a spinner.
**Changes**:
- Removed the extra filter-dropdown assertion after unused status deletion.
- Kept the source-of-truth assertion that the status chip is removed from Client Card settings.

## 2026-05-24 - Avoid Composite Frame Dialog Locator
**Phase**: Test
**Author**: Cursor AI
**Reason**: Playwright does not allow combining page and frame locators with `or_`; the protected status remained visible after delete attempt.
**Changes**:
- Check page and iframe dialogs separately.
- Treat chip persistence as the required blocked-delete assertion when no dialog is shown.

## 2026-05-24 - Open API Client By ID For Reassignment
**Phase**: Test
**Author**: Cursor AI
**Reason**: The delete scenario creates its validation client via API, so the returned ID is the most stable way to open it for status reassignment.
**Changes**:
- Open the API-created client detail page by returned client ID before changing the status to `Lead`.

## 2026-05-24 - Initial Migration
**Phase**: Steps, script, test
**Author**: Cursor AI
**Reason**: Migrated automation-js custom status delete scenario into autotester.
**Changes**:
- Added Phase 1 steps covering in-use delete blocking and unused status deletion.
- Added Phase 2 script mapping legacy Client Card settings and client detail status behavior.
- Added Phase 3 test using API client setup and UI validation for deletion protection.
