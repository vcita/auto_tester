# Setup — Multistaff appointment scheduling (isolated account)

Mirrors the legacy `multistaff.feature` Background (run per scenario on a fresh account):
`user logged in to automatic account via API` + `user creates staff via Platform API`
(two staff) + `user creates new client via API` + `user creates new service via API`.

## WHAT this setup does

1. Enable the `multistaff_features` flag on the fresh account (so the account is a
   multistaff account — the booking dialog exposes additional-staff selection and the
   meeting page renders the assigned/additional-staff rows). Done before login so the
   loaded profile reflects it.
2. Capture the **owner** staff (uid + display name) from the staff list while the owner
   is still the only staff — this is scenario 2's expected `assigned_staff`.
3. Create two staff via Platform API (each confirmed with a GET staff-list read-back):
   - `user_staff<seq>` — role `user`.
   - `manager_staff<seq>` — role `manager`.
4. Create the client `rina success` via API (confirmed with a GET clients read-back).
5. Create the appointment service `r2p_appointment<seq>` via API — `business_location`
   (f2f), payment "require to pay" (`paid_force`), price 1 — assigned to the owner and
   both new staff so the service is pickable by `user_staff` (scenario 1) and the two are
   addable as additional staff (scenario 2). Confirmed with a GET services read-back.
6. Log in to the fresh account (owner/admin UI session for the tests that follow).
7. Store owner/staff/client/service in `context["multistaff"]` for the tests.

## In scope (UI) vs prerequisite (API)

- UI (in scope, in the tests): scheduling appointments via the BO dialog (incl.
  additional-staff multi-select), removing an additional staff from the meeting, and the
  meeting-page assertions.
- API (prerequisite, here): staff / client / service creation and the multistaff-account
  enablement. The scenario-1 staff switch is API-based (SSO), done in the test.
