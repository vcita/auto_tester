# Changelog - Nest Existing Matter Under Contact

## 2026-06-08 - Initial migration (VCITA2-13952)
- Migrated legacy `user nests matter ...` + `matter exists under contact` + `title shows`.
- Selectors verified live: outer `[data-qa='more-option']` → `[data-qa='nesting']`;
  inner `#clientSearchAutocomplete input` → `.client-row` → `[data-qa='dialog-submit-button']`.
- Title asserted via inner `.matter-name-title` (legacy page-bar title equivalent).
- All waits ≤5s.

## 2026-06-08 - Stabilization (VCITA2-13952)
- Verify in-place after nesting instead of re-opening `/app/clients/{matter_client_id}`:
  once nested, that standalone URL no longer resolves (it became a child matter) and spins
  indefinitely → `open_matter_page` exhausted its retries. The nest helper already waits for
  the contact email to switch, so the page is ready for in-place assertions.
- Verified: 3 clean focused runs + 3/3 stress on integration.
