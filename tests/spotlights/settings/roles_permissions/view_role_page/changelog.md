# Changelog — Open Non-Editable Role Page

## 2026-06-11 — Initial migration (VCITA2-14059)
- Migrated from automation-js `roles-and-permissions.feature` scenario "Open
  non-editable role page".
- Navigate to `/app/settings/roles_and_permissions`, open the `[data-role="Administrator"]`
  role, assert the Save button `[data-qa="save-btn"]` is absent (view mode), per
  legacy `isSaveButtonExist()` === false.
- Selectors sourced from legacy page object `rolesAndPermissions.js`.
