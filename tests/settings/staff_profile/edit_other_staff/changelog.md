# Changelog — edit_other_staff

## 2026-06-09 - Initial Build (migration)
**Phase**: All files
**Author**: Cursor AI
**Reason**: Migrated automation-js staff-profile-page.feature scenario 2 (VCITA2-14004)
**Changes**:
- Created steps.md, script.md, test.py.
- Second staff (role user) created via Platform API in _setup; opened by uid.
- Asserts 3 settings tiles, initial display name/email/Dashboard, full field update,
  Canada country, Inbox homepage, email unchanged, and password field NOT displayed for
  another staff.

## 2026-06-09 - Stabilization (helpers)
**Phase**: test.py, staff_profile_helpers.py
**Author**: Cursor AI
**Reason**: "3 tiles" assertion targeted the wrong page; menu click hung 30s.
**Changes**:
- The "3 settings tiles" landing is the per-staff settings page reached from the Angular
  staff list (`/app/settings/staff`, Frontage iframe) via the row kebab -> "Staff settings"
  (legacy Staffs().goToStaffSettings). The direct `/staff_profile/{uid}` URL renders the
  form (0 tiles), so test.py now opens the landing for the tiles count, then opens the
  profile by uid for the field assertions.
- Menu item clicked via `get_by_role("menuitem", name="Staff settings")` inside the iframe;
  `get_by_text(exact=True)` matched the `md-menu-item` wrapper and hung. Added explicit 5s
  timeouts to hover/kebab/menu so failures surface fast.
- Verified green on the runner (Edit Other Staff Profile passed, landing showed 3 tiles).
