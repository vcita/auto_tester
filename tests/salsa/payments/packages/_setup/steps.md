# Packages (BO) — Subcategory Setup

## Objective
Prepare the isolated account for the back-office package-management tests: log in, connect
the mock payment gateway (needed by the BO take-payment / POS / invoice flows), and create
the shared service prerequisites via API.

## Steps
1. Call: login (isolated account credentials)
2. Connect the mock payment gateway (UI)
3. Create 3 services via API:
   - `service` — suggest-to-pay appointment, $100
   - `service2` — suggest-to-pay appointment, $100
   - `r2p_event` — require-to-pay event, $1
4. Store the services in context for the tests to build packages from.

## Notes
- Clients are created per test (legacy Background runs per scenario), so each test owns a
  fresh client and a clean client-package list.
- Taxes / products / feature-flag changes are created per test that needs them.

## Expected Result
- User is logged in to the isolated account.
- Mock gateway connected.
- 3 services exist and are available in context.
