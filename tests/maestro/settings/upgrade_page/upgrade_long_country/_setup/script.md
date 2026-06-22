# Setup Script — Upgrade Long Country

- `block_trust_seal(page)` → `page.context.route("**://sealserver.trustwave.com/**", abort)`.
- `fn_login(page, context, username, password)` using the isolated account
  credentials from context.
