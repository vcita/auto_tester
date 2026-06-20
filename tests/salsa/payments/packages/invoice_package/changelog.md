# Changelog

## 2026-06-19 - Initial migration (VCITA2-14250)
**Phase**: All files
**Reason**: Migrated from automation-js features/salsa/packages.feature (back-office package management).
**Changes**:
- Created steps.md, script.md, test.py from the legacy scenario via MCP-verified exploration of the current build.
- Reuses tests/salsa/payments/packages/packages_helpers.py (BO package management UI) and shared helpers (account_api, appointment_payments_helpers, cp_payment_actions_helpers, event_payments_helpers).

## 2026-06-20 — Stabilization (VCITA2-14250)

- Root cause of the rotating `TimeoutError: 10000ms ... waiting for navigation to **/app/invoices/**`:
  the invoice send -> create -> client-side redirect is the slowest single navigation in the suite
  and intermittently exceeds NAV_TIMEOUT (10s) on the slow BO surface.
  Fix (navigation-load exception, documented): `invoice_client_package` now (1) waits for the invoice
  wizard title to DETACH first (the concrete send-acknowledged signal — the dialog only unmounts
  once the invoice POST is accepted), then (2) confirms the SPA landed on /app/invoices/ via a
  bounded poll gated on that URL readiness signal, budgeted at INVOICE_NAV_TIMEOUT=20000ms. The poll
  short-circuits if the URL already matched while waiting for the wizard to detach. This is a
  bounded navigation-load exception to the 5s element cap, tied to a concrete readiness signal.
