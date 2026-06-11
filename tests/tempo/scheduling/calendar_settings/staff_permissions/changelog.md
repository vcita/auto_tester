# Changelog: staff_permissions

## 2026-06-04 — Initial migration (VCITA2-13796)

- Migrated from `automation-js/features/tempo/calendar-settings.feature` scenario
  "Calendar Settings Staff Permissions".
- Assertions preserved exactly: owner `{staff selector present, 4 tabs}`; limited staff
  `{no staff selector, 3 tabs}`.
- Reused `create_platform_staff` + `unique_email` (calendar API) and `switch_logged_in_staff`
  (calendar helpers) for staff creation and SSO session switching.
- Side-nav reading added to `calendar_settings_helpers.py` against the Vuetage settings
  iframe, scoped to the side-nav `data-qa` and counting `.grouped-items__group__container__menu-item`.
- Validation (integration): the settings page does not nest the side nav under the
  calendar `#vue_iframe_layout`; resolve the frame by searching all `page.frames` for the
  side-nav `data-qa` instead of guessing an iframe id.
- Validation (integration): right after the SSO staff switch, the settings sub-app can
  stay on its loading spinner so the side nav never mounts within one wait; added a bounded
  reload-retry (max 3 attempts) before reading.
