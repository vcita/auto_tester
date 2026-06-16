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
  icon-font rendering. A layer passes only when icon `total > 0`, the count is
  stable across two polls, and no icon is hidden.
- Intentional deviation from legacy: `total == 0` after the poll window is a
  failure (page/layer never loaded), whereas legacy passes vacuously on zero
  icons. Tightened to avoid false positives; no scope/assertion dropped.
- Bounded waits (documented exceptions to the 5s element cap): goto 30s, Angular
  iframe attach 20s, per-layer poll 30s @ 0.5s, one 1s post-nav settle.
- Validated: stress 10/10 STABLE on integration 2026-06-07.
- Jira: VCITA2-13866.

## 2026-06-07 — Align script.md/changelog with implementation
- script.md claimed zero-icon layers pass (legacy behavior) and "pass as soon as
  hidden is empty", contradicting the code's `total == 0` failure guard and
  count-stability gate. Reworded script.md/changelog to match the actual logic
  and to document the bounded wait budgets. Docs-only; no code change.
