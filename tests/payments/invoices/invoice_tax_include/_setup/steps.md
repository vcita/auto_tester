# Setup — Invoice Tax Include Mode

On a fresh isolated United-States account (mirrors invoices.feature Background + the
scenario's "tax_mode include" Given):
1. Log in to the isolated account.
2. Create the client `first last` via API.
3. Create the paid "display a fee" service ($100) via API.
4. Create a 13% tax via API.
5. Set the account tax mode to `include` via API (verified by read-back).
