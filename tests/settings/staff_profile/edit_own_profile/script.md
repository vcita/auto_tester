# Edit Own Profile — Detailed Script

> Selectors sourced from legacy POV page object
> `automation-js/pages/desktop/Frontage/Settings/staffProfilePage.js` (data-qa
> attributes). Shared logic in `staff_profile_helpers.py`. Validated via runner
> runs on integration (+ failure screenshots / MCP for any unresolved UI).

## Initial State
- Logged in (subcategory `_setup`), `pov_landing_page_routing` denied, owner
  staff captured in `context["staff_profile"]["owner"]`.

## Actions

### Step 1: Open own profile settings
- Navigate to `{app_base}/app/settings/staff_profile` (accepted settings entry,
  same pattern as the merged `business_info` test). Wait for the always-visible
  `[data-qa="staff-display-name-input"]` (avatar div stays hidden when initials render).

### Step 2: Assert initial values
- display_name == owner display_name (dynamic, from API), default_homepage == "Dashboard".
- **CHOSEN** read: input_value() for inputs; homepage value from
  `.v-input:has([data-qa="staff-default-homepage"]) .selection-text` (single v-select on page).

### Step 3: Update all fields + save
- country: click `[data-qa="staff-phone-input_number-prefix"]`, click `.vc-list [data-qa="vc-list-AL"]`.
- mobile/first/last/display/professional title: click → clear → press_sequentially.
- default homepage: click the v-select wrapper
  `.v-input:has([data-qa="staff-default-homepage"]) .v-select__selections` (the inner input
  is pointer-intercepted), click option "Calendar" (`get_by_role("option")`).
- save: click `[data-qa="save-profile-button"]`, then wait for it to re-disable (pristine =
  save round-trip done; POV has no `[data-qa="success-toast"]`).

### Step 4: Re-open + assert persisted
- Re-navigate to read back; assert all updated values + country_name "Albania"
  (data-country-name attr) + password_field "displayed" (`[data-qa="staff-password-input"]` present).

## Success Verification
- All updated field values persist on re-read; password field present for own profile.
