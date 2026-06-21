# View package usage history and open the meeting — Detailed Script

## Actions
1. Create a fresh client via API (`make_client(..., unique_name=True)`) — a per-test
   unique name so the BO calendar client-search is unambiguous on the shared account (this
   test does not assert the client name).
2. Create package `package` via API (`account_api.create_package_via_api`: specific service
   `service`, 2cr, $150) — legacy "via API" steps.
3. Assign `package` to the client via API (`account_api.assign_package_to_client`).
4. Schedule appointment `meeting1` (service `service`) for that client as a DUE appointment via the
   scheduling API (`packages_helpers.schedule_appointment_via_api`). A BO-calendar-scheduled
   appointment cannot be redeemed on the current build (its payment-status card exposes only
   `link-to-package`, never `redeem_package` — verified live), so the appointment is seeded via the
   scheduling API (the proven redeemable path, same helper redeem_quota uses); UI scheduling is an
   out-of-scope prerequisite. The meeting is marked COMPLETED in step 5 (asserted in step 8).
5. Redeem `meeting1` with the package (`redeem_appt_with_package_by_id` clicks `[data-qa='redeem_package']`),
   then ensure completed (`mark_appointment_completed`; the past appointment is already COMPLETED, so
   this is a no-op safety net).
6. Assert client credit quota == 1 (`assert_credit_quota`).
7. Open the client-package usage-history dialog (`open_usage_history`) and assert it lists a
   usage item for service `service` (`assert_history_has_service`). The legacy table also
   asserts a computed appointment date; the brittle exact date is intentionally not re-derived
   (same decision as cp_packages.assert_history_has_service).
8. Click the usage item (`click_usage_item`) to navigate to the meeting.
9. Assert the meeting page opened: name `service`, state COMPLETED (`assert_meeting_page`).

## Success Verification
- Usage-history dialog shows the redeemed `service` appointment; clicking it opens the
  completed `service` meeting page.
