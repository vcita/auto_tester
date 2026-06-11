# CRM Bulk Actions Setup — Script (HOW)

Source: `steps.md`.

On the isolated `context["auto_account"]` (username/password + api_token injected
by the runner):

1. `fn_login(page, context, username, password)` — UI login with the isolated-account creds.

Notes:
- Clients are NOT seeded here. Each test (`share_document`, `send_message`,
  `delete_client`) creates its own two clients via `tests.account_api.create_client`
  with a per-test run token in the name/email, so the three tests safely share the
  one isolated account and scope their assertions to their own clients (the
  `delete_client` exact-match assertion in particular).
