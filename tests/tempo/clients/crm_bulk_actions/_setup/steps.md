# CRM Bulk Actions Setup — Steps (WHAT)

Migrated from `automation-js/features/steps/crm-bulk-actions.feature` Background.

The legacy Background creates a fresh account and logs in for **each** scenario.
The closest autotester primitive is an isolated-account subcategory: the runner
provisions one fresh account for the subcategory run, and this setup logs into it.

1. Log in to the isolated automation account.

Each test creates its own two clients via the account API (mirroring the legacy
per-scenario `user creates new client via API`), so no clients are seeded here.
