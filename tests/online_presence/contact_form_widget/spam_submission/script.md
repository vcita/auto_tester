# Script — Spam Client Contact Form Submission

Helpers: `tests/online_presence/contact_form_widget/contact_form_helpers.py`.

## Frame topology
- Client card: `page -> iframe[title="angularjs"] (outer Angular) -> #vue_iframe_layout (inner Vue)`.
  - More menu + mark-spam dialog: outer Angular frame.
  - Conversation pane: inner Vue frame.
- Contact-form widget: customize page nests a preview iframe; the public form
  fields live in the deepest frame, resolved at runtime by scanning `page.frames`
  for `#first_name` (robust to nesting depth).

## Flow
1. **Mark as spam** (`mark_client_as_spam`)
   - Go to `/app/clients/<client_id>`; wait for `[data-qa='more-option']` (outer frame).
   - Click More -> `[data-qa='spam']` -> confirm `.animation-done button[data-qa='confirm-btn']`.
   - Wait for the confirm dialog to detach (request committed).
2. **Submit contact form** (`submit_contact_form`)
   - Go to `/app/online-presence/customize/contact_form`.
   - Find the form frame (`#first_name`), fill first/last/email/message, click
     `input[value="Submit Message"]`, then confirm the blocking loader
     `#jquery-loader-background` appears (submit fired) and clears (mirrors legacy
     `pollPageForLoader`).
3. **Assert no message** (`assert_no_message_from_client`)
   - Re-open the client card; in the inner Vue frame click the first engagements tab
     **Conversation** (`.tab-title` with text "Conversation").
   - Wait for the pane to load — either a message bubble or the empty wrapper
     (`.no-results-wrapper, .bubble-row`, = legacy `conversationBubblesLoaded`).
   - Assert there are **0** `.bubble-row` and the empty state `.no-results-wrapper`
     is visible. Re-check up to a bounded SETTLE_TIMEOUT; any bubble appearing fails
     immediately.

## Non-vacuousness
- A control run that **skips** mark-as-spam was executed during exploration: the same
  submit flow produced a `.bubble-row` ("hello" + form fields) in the Conversation tab
  within seconds. This proves the negative assertion is meaningful (a non-dropped
  message would be detected), so the spam path's empty conversation is a real signal.

## Selector policy
- data-qa first (`more-option`, `spam`, `confirm-btn`). The public widget form and
  conversation pane reuse stable legacy ids/CSS (`#first_name`/`#email`/…,
  `.tab-title`, `.bubble-row`, `.no-results-wrapper`) — no data-qa exists; suggest
  adding them in product code.

## Waits
- Element/interaction waits capped at 5s (UI_TIMEOUT). FRAME_TIMEOUT (10s) is the
  nested-frame render budget; SETTLE_TIMEOUT (10s) is the bounded eventual-consistency
  budget for the spam drop before the negative assertion.
