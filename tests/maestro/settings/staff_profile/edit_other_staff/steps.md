# Admin Edits Another Staff's Profile

Migrated from `automation-js/features/maestro/staff-profile-page.feature`
scenario **Admin opens other staff profile page and updates data** (VCITA2-14004).

## Objective
Verify the admin can open another staff member's profile from the staff settings,
see that staff's details, update every editable field, and that the saved values
persist on re-read — without exposing a password field for another staff.

## Steps
1. Create a second staff member (role "User") via the Platform API:
   name "user_staff", a unique email.
2. Navigate to that staff member's settings via the staff menu in the UI.
3. Verify "3" settings tiles are displayed for the staff.
4. Verify the staff profile shows the display name "user_staff", the staff's email,
   and a default homepage of "Dashboard".
5. Update the staff profile: set country to Canada, display name "User Staff Modified",
   first name "User", last name "Staff_Modified", mobile number "0525555555",
   professional title "Lead User", and default homepage "Inbox". Save.
6. Re-read the profile and verify all updated values persisted: display name, first name,
   last name, mobile number, professional title, default homepage "Inbox", country
   "Canada", the email unchanged, and that the password field is NOT displayed (other staff).
