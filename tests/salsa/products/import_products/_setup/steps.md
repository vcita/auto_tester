# Excel Import Setup - Steps

## Objective
Prepare an isolated account where products can be imported: enable the
`import_products` feature flag, create a tax (for assignment during import),
and log in.

## Preconditions
- Runner created an isolated account and injected `username`, `password`,
  `auto_account`, `api_base_url`, `base_url` into context.
- `VCITA_ADMIN_TOKEN` is available (from `.env`).

## Steps
1. Enable the `import_products` feature flag (before login) and reset the cache.
2. Create a tax `ImportTax` at 13% via API (mirrors the legacy Background tax).
3. Log in to the isolated account.

## Expected Result
- After login the products settings page exposes the Import action and the tax is
  available to assign during import.
