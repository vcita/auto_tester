# Nest Existing Matter Under Contact - Script

> Status: Verified live on integration 2026-06-08 (VCITA2-13952)

## Initial State
- Logged in; `matter_client_id|name`, `contact_client_name|email` in context.

## Actions (`matters_helpers.nest_matter_under_contact`)
1. Open "matter client" page: `page.goto(base + /app/clients/{matter_client_id})`.
2. Outer Angular frame: click `[data-qa='more-option']` (More) → `[data-qa='nesting']`
   ("Move client under…").
3. Nesting dialog (inner Vue frame): fill `#clientSearchAutocomplete input` with the
   contact name; click the `.client-row` filtered by the contact name; click
   `[data-qa='dialog-submit-button']` ("Confirm"); wait confirm hidden.

## Verification (in-place)
- After confirming, the nest helper waits in-place for inner
  `.tooltips-wrapper .info-row_text-value` to switch to the contact email (nest committed).
- Verify on the same page (do NOT re-open `/app/clients/{matter_client_id}`: once nested
  it is a child matter and that standalone URL no longer resolves — it spins indefinitely):
  inner `.matter-list-row` contains "matter client", contact email == contact client email,
  and `expect_title` → inner `.matter-name-title` text == "matter client" (legacy `title shows`).

## Selector notes
- More menu + nesting + nesting-confirm expose stable `data-qa`.
- Nesting search input is `#clientSearchAutocomplete input`; rows are `.client-row` (no data-qa);
  suggested product data-qa: `data-qa="nesting-client-row"`.
