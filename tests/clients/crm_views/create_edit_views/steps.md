# Create And Edit Views

## Objective
Verify a business admin can create, describe, edit and delete CRM views, and that
staff-level permission rules are enforced (view visibility + edit/delete availability)
for a user-role staff.

## Prerequisites
- From `_setup`: fresh account, admin logged in, "Staff User" (role user) created,
  default tabs ("New inquiries", "Open payments", "All") closed.

## Steps
1. As admin, create three views:
   - "account view" — description "description1" — level account
   - "account view 2" — description "description2" — level account
   - "staff view" — description "description3" — level staff
2. Verify the "account view" menu shows description "description1".
3. Verify the "account view" menu shows the account-level permission ("visible to all staff").
4. Verify the "staff view" menu shows the staff-level permission ("visible only to you").
5. Switch the logged-in staff to "Staff User" (via API/SSO).
6. As the staff, close the default "New inquiries" tab and select the "account view".
7. Verify the "staff view" is NOT available to the staff (not pinned and not in the views dropdown).
8. Verify the "account view" menu shows that edit and delete are NOT available to the staff.
9. Switch back to the admin (via API/SSO).
10. As admin, edit "account view": rename to "now staff", description "description1 new", level staff.
11. Verify the "now staff" menu shows description "description1 new".
12. Verify the "now staff" menu shows the staff-level permission.
13. As admin, delete the "staff view" view.
14. Verify the "staff view" is NOT available (it was deleted).
15. Switch the logged-in staff to "Staff User" again (via API/SSO).
16. Verify the "now staff" view is NOT available to the staff (staff-level, owned by admin).
17. Verify the "account view 2" menu shows that edit and delete are NOT available to the staff.

## Expected Result
- All three views are created with the correct description and permission level.
- Editing updates both the description and the permission level (verified in the menu).
- Deleting removes the view.
- A user-role staff cannot see another staff's staff-level views and cannot edit/delete
  account-level views owned by the admin.

## Context Updates
- None (single self-contained scenario).
