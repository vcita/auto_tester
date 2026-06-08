# Changelog - Navigate Matter From List

## 2026-06-08 - Initial migration (VCITA2-13952)
- Migrated legacy `user clicks on matter ... from matter list` + `title shows`.
- Selectors verified live: inner `.matter-list-row` (filtered by name) click; assert
  inner `.matter-name-title`.
- All waits ≤5s.

## 2026-06-08 - Stabilization (VCITA2-13952)
- Open the shared contact page `/app/clients/{contact_client_id}` (the nested matter's own
  URL no longer resolves post-nest). Click "matter client" then "contact client" rows,
  asserting the title follows each — proves list navigation and preserves the legacy
  `title shows "contact client"` assertion.
- Note: the legacy single-click step was flaky (title lagged the click; failed ~2/3 legacy
  runs). `expect_title` auto-retries within 5s, removing that race.
- Verified: 3 clean focused runs + 3/3 stress on integration.
