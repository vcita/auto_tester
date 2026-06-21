# Changelog

## 2026-06-20 — Schedule meeting1 via the scheduling API so it is redeemable (VCITA2-14250)
**Phase**: test.py, script.md, steps.md
**Reason / changes**:
- LIVE FINDING (full-group integration runs, on-failure data-qa dumps): a BO-calendar-scheduled
  appointment cannot be redeemed on the current build — its payment-status card exposes only
  `[data-qa='link-to-package']`, never `[data-qa='redeem_package']`. The redeem button only appears
  for an appointment created via the scheduling API (POST /business/scheduling/v1/bookings) with a
  SPECIFIC-type package (this test already creates the package specific via API). So `meeting1` is
  now seeded via `packages_helpers.schedule_appointment_via_api` (the same helper redeem_quota uses)
  instead of the BO calendar `tempo multistaff_helpers.schedule_appointment(completable=True)`.
  UI scheduling is treated as an out-of-scope prerequisite (as appointment_payments/packaged_service
  documents). The redeem -> quota==1 -> usage-history -> open-completed-meeting coverage is unchanged.

## 2026-06-19 - Initial migration (VCITA2-14250)
**Phase**: All files
**Reason**: Migrated from automation-js features/salsa/packages.feature (back-office package management).
**Changes**:
- Created steps.md, script.md, test.py from the legacy scenario via MCP-verified exploration of the current build.
- Reuses tests/salsa/payments/packages/packages_helpers.py (BO package management UI) and shared helpers (account_api, appointment_payments_helpers, cp_payment_actions_helpers, event_payments_helpers).

## 2026-06-19 - Stabilization (VCITA2-14250)
**Phase**: test.py, script.md, steps.md, packages_helpers.py
**Reason / changes**:
- Unique client name: this test selects the client by NAME via the BO calendar scheduler, but the
  shared isolated account accumulates an identical "first last" client per test, so the scheduler's
  name search matched many buttons (Playwright strict-mode violation). `make_client(unique_name=True)`
  gives a per-test unique name; this test does not assert the client name.
- Explicit package redemption: on the current build, scheduling an appointment for a client holding
  a covering package does NOT auto-apply the package (the appointment is created NOT YET DUE /
  payable, quota unchanged). The credit is consumed only when the appointment payment request is
  explicitly redeemed with the package ("Redeem with package", `[data-qa='redeem_package']`), so the
  test now redeems with the package (new helper `redeem_appt_with_package_by_id`) before/with the
  mark-completed step. Quota coverage (2->1->2->2 / 1) preserved; documented product-behaviour change.

## 2026-06-19 - Stabilization v2: schedule a completable (DUE) appointment (VCITA2-14250)
**Phase**: test.py, script.md, steps.md, multistaff_helpers.py
**Reason / changes**:
- The "Redeem package" action (`[data-qa='redeem_package']`) is gated on the appointment's payment
  request being DUE — on a FUTURE (NOT YET DUE) appointment the redeem button is absent (only
  `link-to-package`), so `redeem_appt_with_package_by_id` could not find it. Step 8 also asserts the
  meeting is COMPLETED, which a future appointment is not.
- Fix: schedule meeting1 with `completable=True` (new shared `schedule_appointment` option that
  schedules in the PAST -> request DUE/OVERDUE + meeting COMPLETED). The redeem button is then present
  and the COMPLETED assertion holds. `mark_appointment_completed` becomes a no-op safety net. No scope
  or assertion change.
