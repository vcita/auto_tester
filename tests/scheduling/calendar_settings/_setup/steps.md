# Setup — Calendar Settings

Preconditions for the calendar-settings scenarios, mirroring the legacy feature
Background (minus the unused client).

## Steps

1. Log in to the isolated account (UI), using the account credentials from context.

## Notes

- The isolated account owner is an admin, satisfying both scenarios' owner-view
  expectations (Business settings access + staff management permission).
- The legacy Background also creates a client (Chuck Norris) and a staff member.
  The client is never referenced by any scenario, so it is omitted. The staff member
  is only needed by `staff_permissions`, so it is created in that test rather than here.
