# Script — Create Client Through All Channels

Helpers: `client_create_helpers.py` (CRM + email infra), `client_create_channels.py`
(livesite + client portal), and the reused `online_presence/contact_form_widget/
contact_form_helpers.submit_contact_form`.

## Surfaces
- **CRM** `/app/clients` — POV Vue page, no iframe. `+ New` (`[data-qa="new-button"]`)
  → `[data-qa="more-actions-button_new_matter"]` → dialog (`name=first_name/last_name/
  email`, Save) → `[data-qa="CrmTable-All-actionBar-searchBar"]`, rows
  `[data-qa="CrmTable-All-item-matter_name"]`.
- **API** — `account_api.create_client`.
- **Livesite** — public Vitrage site `{vitrage}/site/<pivot_uid>` where `vitrage` follows
  the auto_tester convention (app.meet2know→live.meet2know, app.vcita→live.vcita, fenv
  app-<name>→vitrage-<name>); Leave-details action → `cp_iframe` form (label-based fields)
  → Submit.
- **Email** — internal `/infra/automation/message/content?business_uid=<pivot>` with a
  directory token minted via admin `POST /platform/v1/tokens` (legacy api/email.js parity).
  `assert_email_with_subject` is count-aware: the duplicate client "Thank you for your
  message" (sent by both livesite and widget) requires `min_count=2` on the widget pass so
  it cannot re-assert the livesite email.
- **Contact-form widget** — reused C3 submit.
- **Client portal** — Client Portal editor `/app/client-portal-editor` → "View as demo
  client" (opens a popup window) → conversation page (`[data-qa="headerChatBtn"]`) →
  assert a `[data-qa="bubble-header"]` titled `Hi Contact Request`. The leave-details
  email is the business owner's own address, so the conversation lands in the owner's
  demo client portal (legacy "You as a client"). Frame lookups scan `page.frames` to
  tolerate angular/vue iframe nesting.

## Flow
Per channel: create → assert CRM searchable; for the two inbound channels also assert
the client + business emails (bounded polling for the email pipeline) and (livesite)
the client-portal conversation (positive assertion — must find the bubble header).

## Waits
- Interaction waits capped at 5s; CRM page/load at 15s (POV bundle); email polling is
  bounded (30 × 3s) for inbound-pipeline eventual consistency; CRM search retried within
  a bounded budget for search-index lag; portal conversation polled within a bounded 20s
  budget for message propagation.

## Verified (instrumented + 3 clean focused runs)
- New-CRM dialog renders inside the nested Angular iframe; frame located by scanning
  `page.frames` for `#first_name`; Save = `button:has-text("Save")`.
- Livesite leave-details: action link `a.business-action[href*="leave-details"]`; form
  in `cp_iframe` with label-anchored fields; Submit confirmed by loader cycle.
- Client-portal conversation via view-as-demo-client popup confirmed showing
  `Hi Contact Request`.
