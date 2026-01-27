# Changelog: create_user

## 2026-01-26 - Added missing validation (why first-time setup wasn't completed)

**Phase**: test.py  
**Reason**: Accounts created with `create_user` could still show the "Welcome to vcita!" dialog on next login, causing tests (e.g. Create Matter) to fail with "Could not find form frame with 'First Name'". Root cause: the script required "logout, then second login, assert no dialog" but the code never ran that step, so we never detected incomplete onboarding.

**Root cause**:
- **Validation step was never called**: script.md and steps.md (and discovery) require logout → login again → assert no onboarding dialog for 10s. The implementation had `_assert_no_dialog_after_login` but never called it; after `_dismiss_onboarding_dialogs` it set `created_user_ready = True` and returned. So if dismissal failed or timed out (e.g. Welcome fill failed, or dialog didn't appear in time), config was still updated and the account was left in onboarding state.
- **Welcome wait result ignored**: `_wait_for_welcome_dialog` could return False (dialog never appeared in 30s); the code ignored it and ran dismissal anyway, then exited on idle without completing onboarding.

**Fix applied**:
- After `_dismiss_onboarding_dialogs`, call `fn_logout`, then `fn_login` with same credentials, then `_assert_no_dialog_after_login`. If any onboarding dialog appears on second login, create_user now fails instead of updating config.
- If `_wait_for_welcome_dialog` returns False, raise `ValueError` so create_user fails with a clear message instead of continuing.

**Changes**: test.py (validation block; check _wait_for_welcome_dialog return value). Docs: context.md, create_matter script/steps, heal.mdc — document that test account must have completed first-time setup and that seeing the Welcome dialog when debugging means the account isn't ready.

## 2026-01-25 - Initial Implementation

**Phase**: steps, script, test
**Reason**: Switch setup plan - create user and onboard (dismiss one-time dialogs, validate second login).

**Changes**:
- Added steps.md and script.md from discovery (docs/plans/create_user_discovery.md).
- Implemented test.py: fn_create_user with signup (login page → Sign Up link → form → Let's go), optional onboarding_only; dismiss dialogs loop. (Validation step—logout + second login + assert no dialog—was added 2026-01-26.)
- Default password vcita123; params: email, password, name, base_url (login URL = base_url + "/login"), onboarding_only.
