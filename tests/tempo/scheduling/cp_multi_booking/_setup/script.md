# CP Multi-Booking — Category Setup — Detailed Script

> Migrated from multi-booking.feature Background (VCITA2-14228). API setup only.

## Actions (all API)
1. `enable_features(context, "multi_appointment_client_booking")` — legacy FF.
2. `first_staff_uid(context)` — cache the owner staff uid before adding staff.
3. `create_client(context, "Chuck", "Norris", "test23+<seq>@vmeetme.com")`.
4. `create_service_via_api(context, "service1", duration=20)`.
5. `create_service_via_api(context, "service2", duration=40)`.
6. `create_platform_staff_via_api(context, "Staff1", ..., role="user")`.
7. `create_platform_staff_via_api(context, "Staff2", ..., role="user")` (uid saved for service4).
8. `enable_multi_booking(context)` — PUT `/v2/settings {allow_client_multi_booking: true}`,
   read back via GET `/v2/settings` (eventual-consistency guard).
9. `fn_login(page, context, ...)` — business session (parity with legacy background).

## Context Updates
- `mb.client`, `mb.service1`, `mb.service2`, `mb.staff2`, `mb.seq`.
