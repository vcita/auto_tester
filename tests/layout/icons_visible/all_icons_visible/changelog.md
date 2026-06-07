# Changelog — all_icons_visible

## 2026-06-07 — Initial migration
- Migrated from automation-js `features/spotlights/icons.feature`
  (`Scenario: Icons shown in all the iframes`, Spotlights team).
- Verifies design-system icons render (none present-but-hidden) across the POV /
  Angular / Vue iframe layers on dashboard, inbox, calendar, and CRM.
- Icon selectors and per-page iframe-layer mapping mirror the legacy `Layout`
  page object (`pages/desktop/Frontage/layout.js`) and `pageIframeLayers`
  (`pages/Enums.js`).
- Hidden detection done via a single per-frame `evaluate` (querySelectorAll +
  `isDisplayed`-equivalent check), with per-layer polling to absorb lazy
  icon-font rendering.
- Jira: VCITA2-13866.
