# Edit Other Staff Profile — Detailed Script

> Selectors sourced from legacy POV page object
> `automation-js/pages/desktop/Frontage/Settings/staffProfilePage.js`. Shared
> logic in `staff_profile_helpers.py`. Validated via runner runs on integration.

## Initial State
- Logged in as admin (subcategory `_setup`); second staff (role user) created in
  setup, stored in `context["staff_profile"]["user_staff"]` ({uid,name,email}).

## Actions

### Step 1: Assert 3 settings tiles (per-staff settings landing)
- Open the per-staff settings landing via the Angular staff list: navigate
  `{app_base}/app/settings/staff` (Frontage iframe `iframe[title="angularjs"]`),
  hover the staff row, click its kebab (`button[aria-haspopup='true']`), click the
  menuitem "Staff settings" (`get_by_role("menuitem", ...)`). Mirrors legacy
  Staffs().goToStaffSettings.
- Count `.card_inner_content` tiles == 3 (polled in both top-level and iframe contexts;
  the direct `/staff_profile/{uid}` URL renders the form, not tiles).

### Step 2: Open the staff's profile + assert initial values
- Navigate to `{app_base}/app/settings/staff_profile/{staff_uid}`; wait for the
  always-visible `[data-qa="staff-display-name-input"]`.
- display_name == "user_staff", email == created email, default_homepage == "Dashboard".

### Step 3: Update all fields + save
- country CA → "Canada"; mobile/first/last/display/professional title typed;
  default homepage "Inbox"; save `[data-qa="save-profile-button"]` then wait for it to re-disable.

### Step 5: Re-open + assert persisted
- Re-navigate; assert updated values + country_name "Canada" + email unchanged +
  password_field "not displayed" (`[data-qa="staff-password-input"]` absent for other staff).

## Success Verification
- Updated values persist; email unchanged; no password field for another staff.
