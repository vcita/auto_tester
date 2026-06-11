# Staff Role Management — Detailed Script

> Selectors sourced from legacy page objects
> `automation-js/pages/desktop/Frontage/Settings/rolesAndPermissions.js` and
> `.../Frontage/staffs.js`. Shared logic in `roles_helpers.py`. Validated via
> runner runs on integration (+ failure screenshots / MCP for any unresolved UI).

## Initial State
- Logged in (subcategory `_setup`); staff "user_staff" (role User) exists,
  captured in `context["roles_permissions"]["user_staff"]`.

## Actions

### Step 1: Open Edit staff permissions for the staff
- Navigate to `{app_base}/app/settings/staff` (Angular staff list inside
  `iframe[title="angularjs"]`). Wait for `.cards-list-container`.
- Hover the staff row (`//div[text()~name]/ancestor::div[list-item]`), open the
  kebab `button[aria-haspopup='true']`, click menuitem "Edit staff permissions".
  This navigates the top-level app to the POV role page (`.role-page__header`).

### Step 2: Assert name + current role
- `.role-page__header` `data-staff-name` == "user_staff".
- Selected role text `.role-picker .selection-text` == "User".

### Step 3: Change role to Manager
- Click the role picker `.role-picker` (Vuetify v-select), choose option
  "Manager" (`get_by_role("option")`), click Save `[data-qa="save-btn"]`.
- Wait for the role selection text to read "Manager" (persisted signal).

### Step 4: Verify in the staff list
- Navigate back to `/app/settings/staff`, find a staff row containing both
  "user_staff" and "Manager" (`//dnd-nodrag[contains(.,name) and contains(.,role)]`).

## Success Verification
- Role page shows name "user_staff" + role "User" initially; staff list shows
  "user_staff" with role "Manager" after the change.
