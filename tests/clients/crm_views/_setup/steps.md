# CRM Views Setup

## Objective
Prepare a fresh isolated account for the CRM views test: one extra user-role staff exists,
the admin is logged in, and the default CRM tabs are closed.

## Prerequisites
- Isolated account (runner-provisioned) with username/password and API token in context.

## Steps
1. Capture the account owner staff (admin) before creating any extra staff.
2. Create one staff member "Staff User" (role: user) via API.
3. Log in to the account as the admin (owner) through the UI.
4. Open the clients list.
5. Close the default "New inquiries" tab.
6. Close the default "Open payments" tab.
7. Close the default "All" tab.

## Expected Result
- The account has an owner staff and a "Staff User" staff.
- Admin is logged in and on the clients list with the 3 default tabs closed.

## Context Updates
- Save `crm_views.owner` (owner staff) and `crm_views.staff_user` (created staff) for the test.
