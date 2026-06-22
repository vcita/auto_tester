# CRM Selection Logic Setup — Script (HOW)

Source: `steps.md`.

On the isolated `context["auto_account"]` (username/password + api_token injected by
the runner):

1. `fn_login(page, context, username, password)` — UI login with the isolated-account creds.

Notes:
- No clients are seeded here. The `selection_counts` test creates its 12 clients via
  `tests.account_api.create_client`, because the exact summary counts ("OF 12 / OF 11
  CLIENTS") require the account to contain exactly those clients — guaranteed by the
  fresh isolated account.
