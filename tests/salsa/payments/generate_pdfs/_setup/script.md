# Script — Generate PDFs Setup

Phase 2 (HOW). API-only; no page interaction.

## Step 1 — Create shared client
```python
client = create_client(context, "first", "last", f"test+{stamp}@vmeetme.com")
context["pdf_client"] = client
context["pdf_client_id"] = client["id"]
```
`create_client` → `POST /platform/v1/clients`, returns the client (id) and portal token.
Stored on context for the three PDF subcategory tests.
