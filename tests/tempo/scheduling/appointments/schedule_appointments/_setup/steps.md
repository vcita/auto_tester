# Setup: Schedule Appointments (isolated account)

Mirrors the legacy `scheduling-appointments.feature` Background on a fresh isolated account.

## Steps

1. Capture the account **owner** staff (before creating extra staff) via Platform API.
2. Create **user_staff** (role `user`) via Platform API.
3. Create client **Chuck Norris** via API and confirm it persists (GET read-back).
4. Create the **service1** appointment service (assigned to owner + user_staff) via API.
5. Log in to the isolated account as the owner.
6. Store `owner`, `user_staff`, `client`, `service`, `seq` under `context["schedule_appts"]`.

## Notes

- Per-scenario prerequisites (inline new client/staff during scheduling, the arrival-window
  `service2`, additional recipients) are created inside the individual tests, matching the
  in-scope UI behavior being migrated.
- The account is isolated (`account_profile.type: isolated`, `cleanup: always`), so no
  parent-category setup runs and the account is torn down after the subcategory completes.
