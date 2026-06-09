# Invoice Late Fee (UI) Setup - Steps

## Objective
Log in to the isolated US account and create, via API, the client (`first last`, with a
captured client-portal token) and the `display a fee` service ($100) the late-fee invoice
scenario builds on.

## Prerequisites
- Runner created an isolated US account (`country_name: United States`).
- `context["username"]`, `context["password"]` are available.

## Steps
1. Log in to the isolated account.
2. Create client `first last` (`test+<ts>@vmeetme.com`) via API; capture its portal token.
3. Create a paid "display a fee" service priced at 100 via API.

## Expected Result
- Logged in; client exists with a portal token; service exists.
- `context` holds `created_client_id`, `created_client_name`, `created_client_email`,
  `client_portal_token`, `invoice_service_name`.
