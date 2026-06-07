# Layout Category Setup — Script

## Goal
Prepare an isolated account so the icon-visibility test can navigate the main
frontage pages with the POV new dashboard enabled.

## Steps
1. `enable_features(context, "new_dashboard")` — whitelist the new-dashboard flag
   via the admin feature-flags API (so `/app/dashboard` resolves to the POV
   layer used by the legacy `pageIframeLayers` mapping).
2. `fn_login(page, context, username, password)` — UI login with the
   harness-provided account credentials.

## Notes
- `username` / `password` are injected into `context` by the runner before setup.
- No UI navigation here; each test navigates to its own page(s).
