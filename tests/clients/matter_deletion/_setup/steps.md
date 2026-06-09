# Matter Deletion Setup - Steps

## Objective
Log in to the isolated account and create a contact (`contact last`) via API so the test
starts with a contact that owns a single default matter.

## Prerequisites
- Runner created an isolated account.
- `context["username"]`, `context["password"]`, and `context["auto_account"]` are available.

## Steps
1. Log in to the isolated account.
2. Create a contact `contact last` (`contact+<ts>@vmeetme.com`) via the platform clients API.

## Expected Result
- Logged in; the contact exists with one default matter named `contact last`.
- `context["contact_id"]` / `context["contact_email"]` are set for the test.
