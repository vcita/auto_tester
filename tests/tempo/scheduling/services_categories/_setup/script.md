# Setup script — Categories & services

`setup_services_categories(page, context)`:

1. Read `username`/`password` from context (injected by the runner for the isolated
   account). Raise if missing.
2. `fn_login(page, context, username, password)`.
3. `goto_services(page)` — navigate to `/app/settings/services`, wait for the
   `Settings / Services` heading and the first category card.
4. For each of `Demo class / event`, `In-office appointment`, `Introductory phone call`:
   wait for the exact text to be visible (≤5s).
5. Store `context["default_services"]`.
