# Open Non-Editable Role Page — Detailed Script

> Selectors sourced from legacy POV page object
> `automation-js/pages/desktop/Frontage/Settings/rolesAndPermissions.js`
> (data-qa / data-role attributes). Shared logic in `roles_helpers.py`.
> Validated via runner runs on integration (+ failure screenshots / MCP for any
> unresolved UI).

## Initial State
- Logged in (subcategory `_setup`).

## Actions

### Step 1: Open the Roles & Permissions page
- Navigate to `{app_base}/app/settings/roles_and_permissions` (accepted settings
  entry, same pattern as the merged `staff_profile`/`business_info` tests).

### Step 2: Open the Administrator role
- Click the role row `[data-role="Administrator"]`, wait for the role page header
  `.role-page__header` to be visible.

### Step 3: Assert view mode
- Assert the Save button `[data-qa="save-btn"]` is NOT present (legacy
  `isSaveButtonExist()` === false for view mode). A built-in role has no editable
  Save action; an editable role would render it.

## Success Verification
- `is_save_button_present(page)` is False on the Administrator role page.
