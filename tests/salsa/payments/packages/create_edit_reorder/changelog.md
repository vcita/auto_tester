# Changelog

## 2026-06-19 - Initial migration (VCITA2-14250)
**Phase**: All files
**Reason**: Migrated from automation-js features/salsa/packages.feature (back-office package management).
**Changes**:
- Created steps.md, script.md, test.py from the legacy scenario via MCP-verified exploration of the current build.
- Reuses tests/salsa/payments/packages/packages_helpers.py (BO package management UI) and shared helpers (account_api, appointment_payments_helpers, cp_payment_actions_helpers, event_payments_helpers).

## 2026-06-19 - Stabilization: gate package-list assertion on API read-back (VCITA2-14250)
**Phase**: packages_helpers.py (assert_package_in_list)
**Reason / changes**:
- Intermittent failure "Package 'package_1' did not appear in the list": the Settings/Packages list
  lags the create write, and the prior UI reload-and-recheck (≤3 attempts at ~1s) was sometimes too
  short.
- Fix within the rules: `assert_package_in_list` now first confirms the package write propagated via a
  bounded API read-back (`_wait_package_exists_api`, polling `get_package_id_by_name` — the documented
  eventual-consistency exception), THEN reloads the Settings list and asserts within the project ≤2-retry
  cap. The wait now sits on the API read-back, not on extra UI reloads; mirrors the API-readback pattern
  already used for the client-package card. No scope or assertion change.
- Hardened the create-form md-autocomplete pick (`_select_autocomplete`): a suggestion click that landed
  during a list re-render was being silently dropped, leaving the input's raw typed text (red-underline
  invalid) and the dependent quantity field (`#specificServiceQuantity` / `dummyProductQuantity`)
  DISABLED, so the next `_type(quantity)` timed out (observed live: "New Package" form with product
  "payable_item1" selected but No. of products empty). The pick now verifies it COMMITTED by waiting for
  the single-select suggestion list to collapse, retrying the type+pick within the existing ≤2-retry cap.
  The ANY-service multiselect picker (whose overlay intentionally stays open) opts out via a new
  `expect_commit=False` arg, so create_assign_* / pay_* any-service flows are unaffected.
- Hardened `_type` (the form text-entry helper): the AngularJS form occasionally dropped trailing
  characters during an ng digest re-render (observed live: a package typed as "package_1" persisted as
  "package", twice — so neither package_1 nor package_2 appeared in the list). `_type` now reads the
  value back after typing and re-types once if it did not stick, bounded at ≤2 retries; numeric fields
  that reformat (e.g. "150" -> "150.00") are accepted via a prefix match. The field value is the
  readiness signal (no fixed sleep).

## 2026-06-20 — Stabilization (VCITA2-14250)

- Root cause of the rotating "Package 'package_1' did not appear in the list": the package-name
  field is AngularJS, and per-char `input` events from `press_sequentially` could have a digest drop
  the trailing chars from the ng-model SCOPE even though the DOM input value was correct — so the
  package SAVED as "package" instead of "package_1" (failure screenshot showed two "package" rows,
  no "package_1"). The `_type` read-back only checked the DOM value, which looked correct, so the
  bug slipped past the existing retype guard.
  Fix: after typing, `_type` now re-dispatches native `input`+`change` events and blurs the field so
  ng-model re-reads the full DOM value into scope before save.
- Additive: `create_package` now tracks the created package id for teardown so the shared isolated
  account does not accumulate stale package rows across stress iterations.
