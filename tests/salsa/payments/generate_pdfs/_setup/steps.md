# Generate PDFs — Setup

Prepares the shared isolated account for all Generate PDFs tests.

## What it does
1. Create the client **first last** via API (no UI login — every PDF scenario is API-only).

## Saved to context
- `pdf_client` — full client dict (id, full_name, email, token)
- `pdf_client_id`, `pdf_client_email`

## Notes
- The legacy `generate_pdfs.feature` Background creates an account + a client via API and
  never logs into the UI; this setup mirrors that exactly. The runner provides the
  isolated account's `api_token`/`pivot_uid`, which is all the billboard PDF calls need.
