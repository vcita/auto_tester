# Changelog — Staff Role Management

## 2026-06-11 — Initial migration (VCITA2-14059)
- Migrated from automation-js `roles-and-permissions.feature` scenario "Staff
  Role page".
- Staff "user_staff" (role User) created via API in `_setup`.
- Open Edit staff permissions via the Angular staff-list kebab (mirrors
  `staff_profile`'s `open_staff_settings_landing`, with menuitem "Edit staff
  permissions"); assert `.role-page__header` `data-staff-name` + `.role-picker
  .selection-text`; change role via the v-select + Save `[data-qa="save-btn"]`;
  verify the staff list row contains name + "Manager".
- Selectors sourced from legacy page objects `rolesAndPermissions.js` + `staffs.js`.

### Scope decision: staff creation prerequisite via API
- The legacy scenario opens with `user creates staff` via the UI, but the feature
  under test here is **role management** (the role page + changing the role). Staff
  creation is a prerequisite, not an assertion of this scenario, so it is created
  via the Platform API in `_setup` (mirrors the sibling `staff_profile` migration).
  Every in-scope action — opening Edit staff permissions, reading name/role, changing
  the role, verifying it in the staff list — stays in the UI. No assertion is lost.
