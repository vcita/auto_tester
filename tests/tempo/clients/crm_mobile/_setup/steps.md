# Setup: CRM Mobile

Prepare an isolated account with the 10 seeded clients from the legacy
`crm_mobile_clients.csv`, then log in as the owner (mirrors the legacy Background:
create account, create new clients via API, log in to automatic account).

## Steps
1. Log in to the isolated account as the owner.
2. Seed the 10 clients from `crm_mobile_clients.csv` via API (first1 last1 .. first10 last10,
   with row 4's first name "no-tag"). Emails are made unique per run.
   - save_to_context: crm_mobile_seq

## Expected Result
- Owner is logged in to the isolated account.
- 10 clients exist in the account, available for the CRM mobile list scenario.
