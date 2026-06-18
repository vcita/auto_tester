# Test: redeem_and_repurchase

## Objective
A client redeems an appointment from an assigned package, sees it fully redeemed with the
booking in its history, and re-purchases it from the finished package.
Migrates the second scenario of automation-js features/salsa/cp/packages.feature.

## Preconditions
Setup created the mock gateway, 3 services, 2 packages and 1 client (with portal token).

## Steps
1. Assign package1 + package2 to the client via API.
2. The client navigates to the purchased-packages page.
3. Start the scheduling flow from package1. → The scheduler services page opens.
4. The services page shows r2p_appointment + s2p_appointment.
5. Schedule a new r2p_appointment (default timeslot, intake confirm).
6. The booking confirmation shows "Confirmed!" and is redeemed with the package.
7. The purchased-packages page shows:
   - package2 | 0/2, s2p_appointment | active | any
   - package1 | 1/1, r2p_appointment s2p_appointment r2p_event | fully_redeemed | any
8. The package1 history dialog shows the redeemed r2p_appointment booking.
9. Re-purchase package1 from the finished package. → The package description page (package1) opens.
10. Purchase the selected package with a NEW card.
11. The purchased-packages page shows:
    - package1 | 0/1, r2p_appointment s2p_appointment r2p_event | active | any
    - package2 | 0/2, s2p_appointment | active | any
    - package1 | 1/1, r2p_appointment s2p_appointment r2p_event | fully_redeemed | any

## Assertions
- Scheduler services list equals the expected services.
- Booking confirmation title + redeemed-with-package mark present.
- Purchased-packages rows match (incl. the same package appearing both active and fully_redeemed).
- The usage-history dialog lists the redeemed service.
