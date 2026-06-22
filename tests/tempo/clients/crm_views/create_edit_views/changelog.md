# Changelog — Create And Edit Views

## 2026-06-08 — Initial migration (VCITA2-13951)
- Migrated automation-js `crm-view-create-and-edit.feature` (single scenario
  "Admin creates and edits views", 24 steps) into one autotester test.
- UI actions kept as UI (ported 1:1 from `newClients.js` with the same `data-qa`
  selectors): create view ×3, three-dot menu reads (description + permission),
  edit view, delete view, close tab, select view, view-availability checks.
- API/SSO only for out-of-scope prerequisites (matching the legacy API/SSO setup):
  staff creation, owner-session end, and the SSO staff-switch — reusing
  `account_api` + `calendar_api` partner-SSO primitives (proven on integration by the
  multistaff/calendar migrations).
- Zero scope loss: all 8 legacy assertions preserved — 3 create-time description/
  permission checks, 2 post-edit description/permission checks, 2 staff visibility
  "not available" checks, and 2 staff edit/delete "not available" checks.
- Permission-enforcement assertions match menu lines by content (not fixed index) so
  the highest-value checks are robust to incidental extra menu lines.

## Legacy baseline
- `node index features/steps/crm-view-create-and-edit.feature --headless`
  → 1 scenario / 24 steps passed, executing steps 2m12.571s (wall 2:14.38), env integration.
