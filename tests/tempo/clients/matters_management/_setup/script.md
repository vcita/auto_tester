# Matters Management Setup - Script

> Status: Verified live on integration (app.meet2know.com) 2026-06-08
> Migrated from automation-js matters-management.feature Background (VCITA2-13952)

## Initial State
- Runner created an isolated auto-account; `username`/`password`/`auto_account`/`base_url`/`api_base_url` in context.

## Actions
1. `fn_login(page, context, username, password)` → lands on `/app/dashboard`.
2. `account_api.create_client(context, "matter", "client", "matter+<ts>@vmeetme.com")`
   → `POST /platform/v1/clients` with `Bearer auto_account.api_token`.
3. `account_api.create_client(context, "contact", "client", "contact+<ts>@vmeetme.com")`.

## Why API for client creation
Client creation is the legacy Background API setup (`user creates new client via API`),
not a tested UI behavior. Kept as API per the migration translation rules.

## Context Updates
- `matter_client_id|name|email`, `contact_client_id|name|email`.
