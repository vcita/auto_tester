# Currency — Setup

API-only setup mirroring the legacy `payments_settings.feature` Background.

## What it does
1. Create a $100 f2f service `test service` via API.
2. Create the client `first1 last1` via API.

## Saved to context
- `currency_service` — service dict (id, name)
- `currency_client` — client dict (id, full_name, token)

## Notes
- No UI login: the currency scenario is fully API-driven.
