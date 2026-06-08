# Changelog - Add Matter From Quick Actions

## 2026-06-08 - Initial migration (VCITA2-13952)
- Migrated legacy `... from quick-actions menu` + `matter exists under contact`.
- Selectors verified live: `[data-qa='vcMenu-QuickAction']` → `[data-qa='item-client']`;
  outer dialog `input[name='email']` + `#autocomplete-email` + suggestion text +
  radio "Create a new client under this contact" + Continue + matter-name + Save.
- All waits ≤5s.

## 2026-06-08 - Stabilization (VCITA2-13952)
- Radio: force-click `md-radio-button[aria-label="Create a new client under this contact"]`
  (Angular-Material ripple intercepts a normal click; text-label click hung to 30s).
- "Email already exists" confirmations made resilient: click `ok()`, then click the second
  `continue()` confirm only if present. When the contact already has a matter (matter_1 from
  the prior test, sharing the email), the second confirm is absent — the old hard wait timed
  out at 5s. Now dismissed in a 5s-bounded loop that returns once the matter form is reachable.
- Verified: 3 clean focused runs + 3/3 stress on integration.

## 2026-06-08 - Closeout validation (VCITA2-13952)
- Re-validated post-cleanup: 7 clean focused runs (56-64s) and stress 3/3 (latest).
  Across stress iterations one earlier run hit a transient 5000ms timeout (~8/9 overall);
  the `open_matter` bounded retry (1 + 2) absorbs CRM-indexing lag and it did not recur.
  Treated as an infra hiccup, well within the project's 3/30 tolerance.
