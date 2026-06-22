# Cancel all multi-booking appointments

Schedule one appointment made of three linked services, cancel all of them at
once, and verify the result.

## Steps

1. Schedule a multi-service (linked) appointment for the client with three
   services (service1, service2, service3). The first service gets tomorrow's
   date at 09:00 AM; the other two inherit it.
2. Open the first linked appointment and cancel all linked appointments (the
   default option in the cancellation dialog).
3. Verify all three appointments are **Cancelled**.
4. Verify the client conversation timeline shows a cancelled linked-booking
   bubble listing the three services with a **CANCELLED** state.
