# Roles & Permissions — Setup

Prepares the isolated account for the roles & permissions tests, mirroring the
legacy feature Background (`user logged in to automatic account via API`) and
scenario 3's staff creation (`user creates staff | user_staff | role User`).

## Steps
1. Create a second staff member "user_staff" with role "User" via the Platform
   API (used by the staff_role test).
2. Log in to the isolated account.
