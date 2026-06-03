# Cancel single multi-booking appointment

Schedule one appointment made of three linked services, cancel only the first
linked appointment, and verify the result.

## Steps

1. Schedule a multi-service (linked) appointment for the client with three
   services (service1, service2, service3). The first service gets tomorrow's
   date at 09:00 AM; the other two inherit it.
2. Open the first linked appointment and cancel only this one (choose the
   "single" option in the cancellation dialog).
3. Verify the first appointment is **Cancelled**, **Free**, and no longer shows a
   multi-service (linked) booking.
4. Verify the other two appointments are still **Scheduled**, **Free**, and still
   linked together, with the linked count now showing **2** and the linked-booking
   list containing both remaining services.
