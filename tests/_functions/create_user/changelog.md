# Changelog: create_user

## 2026-01-25 - Initial Implementation

**Phase**: steps, script, test
**Reason**: Switch setup plan - create user and onboard (dismiss one-time dialogs, validate second login).

**Changes**:
- Added steps.md and script.md from discovery (docs/plans/create_user_discovery.md).
- Implemented test.py: fn_create_user with signup (login page → Sign Up link → form → Let's go), optional onboarding_only; dismiss dialogs loop; logout + login + assert no dialog.
- Default password vcita123; params: email, password, name, base_url (login URL = base_url + "/login"), onboarding_only.
