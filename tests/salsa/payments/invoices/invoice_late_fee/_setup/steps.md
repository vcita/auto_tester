# Setup — Invoice Late Fee

On a fresh isolated United-States account (mirrors invoices.feature Background + the
scenario's "late fee settings" Given):
1. Log in to the isolated account.
2. Create the client `first last` via API.
3. Create the paid "display a fee" service ($100) via API.
4. Create a 13% tax via API.
5. Enable late fees via API: 10% (amount 10 / percent 10), type `percent`, 5 days
   after the due date.
