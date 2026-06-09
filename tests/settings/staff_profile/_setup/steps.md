# Staff Profile — Setup

Prepares the isolated account for the staff profile tests, mirroring the legacy
feature Background (denied `pov_landing_page_routing` flag) and scenario 2's
staff creation.

## Steps
1. Deny the `pov_landing_page_routing` feature flag on the account (API).
2. Capture the account owner staff (display name/email) for the own-profile
   initial assertion (the account name is dynamic per auto-created account).
3. Create a second staff member "user_staff" with role "User" via the Platform
   API (used by the edit_other_staff test).
4. Log in to the account.
