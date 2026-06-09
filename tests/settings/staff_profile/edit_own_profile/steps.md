# Admin Edits Own Staff Profile

Migrated from `automation-js/features/maestro/staff-profile-page.feature`
scenario **Admin opens own staff profile page and updates data** (VCITA2-14004).

## Objective
Verify the admin can open their own profile settings, see their current details,
update every editable field, and that the saved values persist on re-read.

## Steps
1. Open the admin's own profile settings page via the UI.
2. Verify the page shows the admin's current display name (the account display name,
   read from the API) and a default homepage of "Dashboard".
3. Update the profile: set country to Albania, display name "Admin Staff Updated",
   first name "Admin", last name "Staff_Updated", mobile number "0528888888",
   professional title "Senior Administrator", and default homepage "Calendar". Save.
4. Re-open / re-read the profile and verify all updated values persisted: display name,
   first name, last name, mobile number, professional title, default homepage "Calendar",
   country "Albania", and that the password field is displayed (own profile).
