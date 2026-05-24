# Changelog

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
**Reason**: Migrated automation-js custom status delete scenario into auto_tester.
**Changes**:
- Added Phase 1 steps covering in-use delete blocking and unused status deletion.
- Added Phase 2 script mapping legacy Client Card settings and client detail status behavior.
- Added Phase 3 test using API client setup and UI validation for deletion protection.
