# Changelog - Add Matter From Contact Pane

## 2026-06-08 - Initial migration (VCITA2-13952)
- Migrated legacy `... from contact pane` + `matter exists under contact`.
- Selectors verified live on integration: inner `.add-matter-button` (native click),
  outer md-dialog `[ng-click='continue()']`, `f-client-field[field*='matterName'] input`,
  `button:has-text('Save')`; verify via `.matter-list-row` + `.tooltips-wrapper .info-row_text-value`.
- All waits ≤5s; matter-page open uses bounded retry (1 + 2) for transient load slowness.
