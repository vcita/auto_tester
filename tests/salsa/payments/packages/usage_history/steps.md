# View package usage history

## Objective
Verify that a redeemed appointment appears in a client-package's usage-history dialog and that
clicking the usage item navigates to the completed meeting.

## Prerequisites
- Setup created `service`, `service2`, `r2p_event` and connected the mock gateway.

## Steps
1. Create a fresh client via API.
2. Create a package `package` via API: specific service `service`, 2 credits, price 150.
3. Assign `package` to the client via API.
4. Schedule appointment `meeting1` (service `service`) for the client as a DUE appointment via the
   scheduling API (out-of-scope prerequisite: a BO-calendar-scheduled appointment cannot be
   redeemed on this build — its card exposes only `link-to-package`, never `redeem_package`).
5. Redeem `meeting1` with the package (explicit, via the redeem button), then ensure completed.
6. Verify the client's package credit quota is 1.
7. Open the client-package usage-history dialog and verify it lists a usage item for
   service `service`.
8. Click the usage item to navigate to the meeting.
9. Verify the meeting page is opened: name `service`, state `COMPLETED`.

## Expected Result
- The usage-history dialog shows the redeemed `service` appointment.
- Navigating from the dialog opens the completed `service` meeting page.
