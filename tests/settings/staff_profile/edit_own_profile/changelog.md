# Changelog — edit_own_profile

## 2026-06-09 - Initial Build (migration)
**Phase**: All files
**Author**: Cursor AI
**Reason**: Migrated automation-js staff-profile-page.feature scenario 1 (VCITA2-14004)
**Changes**:
- Created steps.md, script.md, test.py.
- Selectors from legacy POV page object (data-qa). Shared logic in staff_profile_helpers.py.
- Initial display-name expectation read from API (owner staff, captured in _setup) since
  the auto-created account name is dynamic.
- Asserts initial Dashboard homepage, full field update, Albania country, Calendar homepage,
  and password field displayed on own profile.

## 2026-06-09 - Stabilization (helpers)
**Phase**: staff_profile_helpers.py
**Author**: Cursor AI
**Reason**: First runner runs timed out on wrong readiness/save signals.
**Changes**:
- Readiness signal switched from `[data-qa="avatarImage"]` (a hidden VcImage div when
  initials render) to the always-visible display-name input.
- Default-homepage control opened via the v-select wrapper
  (`.v-input:has([data-qa="staff-default-homepage"]) .v-select__selections`); the inner
  `<input>` is pointer-intercepted. Value read from the scoped `.selection-text`.
- Save completion now waits for the Save button to re-disable (pristine after save);
  there is no `[data-qa="success-toast"]` in POV.
- Verified green on the runner (Edit Own Profile passed, 5.5s).
