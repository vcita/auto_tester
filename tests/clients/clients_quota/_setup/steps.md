# Setup — Clients Quota

Prepare the isolated, 11-client-capped account so the single test starts one client
below the cap (10/11).

## Preconditions
- Runner provisions an isolated account on an operator package with
  `clients_credit = 11` (see `_category.yaml` `account_profile.operator_package`).

## Steps
1. Log in to the isolated account (UI), mirroring the legacy Background login.
2. Seed 10 clients via API (`first01 last01` … `first10 last10`, unique
   `testNN+<seq>@vmeetme.com` emails) — the legacy "user creates new client via API"
   table. This is an out-of-scope prerequisite, so it runs via API, not the UI.
3. Store the run `seq` and the seeded client names/emails in
   `context["clients_quota"]` for the test (the test deletes `first10 last10`).

## Notes
- Only the 11th client is created through the UI (in the test) — that UI creation is
  the in-scope action that reaches the cap.
