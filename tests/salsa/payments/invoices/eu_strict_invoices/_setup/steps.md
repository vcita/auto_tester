# EU Strict Invoices Setup - Steps

## Objective
Log in to the isolated Italy account and create the invoice prerequisites.

## Prerequisites
- Runner created an isolated account with country `Italy`.
- Automation feature flags are enabled before the country update.

## Steps
1. Log in to the isolated account.
2. Create a client named `first last` via API.
3. Create a paid service priced at `100` via API.

## Expected Result
- The isolated account is logged in.
- The client is available in the invoice client picker.
- The service is available as a billable invoice item.

## Context Updates
- Save `invoice_client_search_term`, `created_client_id`, `created_client_name`, and `created_client_email`.
- Save `invoice_service_name`, `invoice_service_price`, and `invoice_service`.
