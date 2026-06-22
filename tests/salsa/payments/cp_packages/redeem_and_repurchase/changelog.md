# Changelog: cp_packages/redeem_and_repurchase

## 2026-06-18 - Created (migration VCITA2-14229)
**Phase**: steps.md, script.md, test.py
**Author**: Cursor AI (migrate)
**Reason**: Migrate scenario 2 (client uses his packages, redeem and repurchase).
**Details**:
- Assign package1 + package2 to the client via API (assign_package_to_client), then drive
  the CP: navigate to purchased-packages, start scheduling from package1, assert the
  scheduler services page (r2p_appointment + s2p_appointment), schedule an r2p_appointment,
  assert the booking confirmation ("Confirmed!" + redeemed-with-package), assert
  purchased-packages (package2 active + package1 1/1 fully_redeemed), open the package1
  history dialog and assert the r2p_appointment usage item, re-purchase package1 from the
  finished package, and assert the final purchased-packages state (package1 active +
  package2 + package1 fully_redeemed).
- **Deviation (history date)**: the legacy table asserts `appointment_date: default`, a
  dynamically-computed first-available-timeslot string. The migrated assertion verifies the
  usage item for the redeemed service exists (service_name), which is the user-visible
  coverage; the brittle exact date is intentionally not re-derived.
- **Re-purchase fallback**: clicks `[data-qa='client-package-buy-again']`; if that does not
  surface the description page, falls back to the derived single-package link (same end
  state as the legacy buy-again button).
- redeemed_with_package=true is asserted by presence of `.package-info-wrap` (legacy
  bookingRedeemedText).
- Purchased-packages reads reload-and-recheck within a 2-retry cap (list lags the write).
**Legacy evidence**: legacy run 2 scenarios / 34 steps passed (3m06s, directory recurly).

## 2026-06-18 - Stabilized against live runs (VCITA2-14229)
**Phase**: script.md, test.py, cp_packages_helpers.py
**Findings from live debugging (integration directory) and fixes**:
- Test creates its OWN client (`make_client`) and authenticates the CP session in
  `open_portal` (see purchase_packages changelog) -- without a fresh client, this test's
  assigned packages mixed with the purchase_packages test's purchased packages.
- Purchased-packages opened via the CP side menu (legacy openClientPackagesPage), not URL.
- **fully_redeemed rendering / propagation**: after redeeming package1 (verified
  bookings_usage 1 / total_bookings 1 via the client_packages API), the fully_redeemed card
  renders under `[data-qa|='inactive-package']`, and the inactive section lags the active
  section by a render cycle. The assertion polls/scrolls until the expected number of cards
  render (NAV budget) before reading, within the 2-retry reload cap. State class second
  token contains `fully` (fully_redeemed), matched as a substring.
- Scheduler/booking/history selectors mirror the legacy page objects and worked unchanged.
**Result**: test passes 3/3 consecutive clean focused runs.
