# CRM Selection Logic Setup — Steps (WHAT)

Migrated from `automation-js/features/steps/crm-selection-logic.feature` Background.

The legacy Background creates a fresh account and logs in. The closest auto_tester
primitive is an isolated-account subcategory: the runner provisions one fresh account
for the subcategory run, and this setup logs into it.

1. Log in to the isolated automation account.

The single test creates its own 12 clients via the account API and then sets the
rows-per-page and sort, so all client setup lives in the test (not here).
