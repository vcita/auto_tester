# Deposits — Setup

Prepares the shared isolated account for all deposits tests.

## What it does
1. Log in to the isolated account (UI).
2. Create the client **Torry Deposi** via API, capturing the client-portal token
   (used later by the client-portal scenarios).

## Saved to context
- `deposit_client` — full client dict (id, full_name, email, token)
- `deposit_client_id`, `deposit_client_name`, `deposit_client_token`

## Notes
- The `point_of_sale` feature flag is intentionally not set here. The invoice
  scenarios manage it themselves (quick-actions path denies POS, POS path enables it),
  keeping them order-independent on the shared account.
