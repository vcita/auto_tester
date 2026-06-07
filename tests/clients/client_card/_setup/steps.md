# Setup: Client Card (isolated account)

Mirrors the legacy `client-card.feature` Background (`user logged in to automatic account`).

## What it does
1. Log in to the fresh isolated account provisioned for this subcategory.

The isolated account guarantees the Client Card Settings start with no custom
fields (so the fixed field names `client_field`/`contact_field` are free) and the
CRM client list is empty, keeping the filter assertions deterministic.
