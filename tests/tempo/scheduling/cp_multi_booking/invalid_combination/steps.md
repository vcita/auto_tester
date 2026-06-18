# CP Multi-Booking — Invalid Service Combination

## Objective
As an anonymous client, open the scheduler and verify that after selecting one service, the
services that cannot be combined with it become disabled; after deselecting, all services
become enabled again; and selecting an event takes the scheduler to the future-event step.

## Prerequisites
- Category setup ran (client, service1, service2, staff, CP multi booking enabled).
- This subcategory's setup adds service3 (f2f client), service4 (Staff2 only), event1 (event),
  service6, and schedules an instance of event1 via API.

## Steps
1. Open the business livesite and pick the "Schedule Now" action (opens the CP scheduler).
2. In the scheduler services page, select `service1`.
3. Verify the services page shows these services as disabled:
   - `service3` (disabled)
   - `service4` (disabled)
   - `event1` (disabled)
4. Deselect `service1`.
5. Verify the services page shows all of these services as enabled:
   - `service1`, `service2`, `service3`, `service4`, `service6`, `event1`,
     `In-office appointment`, `Introductory phone call`.
6. Select `event1`.
7. Verify the client-portal scheduler's next step is the future-event step ("futureEvent").

## Expected Result
- Selecting service1 disables the incompatible services (service3/service4/event1); deselecting
  re-enables every service; selecting event1 advances to the future-event step.
