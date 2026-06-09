# Changelog — Spam Client Contact Form Submission

## 2026-06-09 — Initial migration (VCITA2-14006)
- Migrated from `automation-js/features/tango/contact-form-widget.feature`
  (Scenario: "spamming client fills up contact form").
- New top-level category `online_presence`; subcategory `contact_form_widget`
  (isolated account). `_setup` logs in and creates the target client via API.
- Scenario (all legacy actions/assertion preserved):
  1. Mark client as spam from the client card (outer Angular frame More menu).
  2. Submit the public contact-form widget (deepest nested preview frame, resolved
     by scanning `page.frames` for `#first_name`).
  3. Assert the client's conversation has no message (inner Vue frame empty state).
- Reuses the POV client-card frame topology proven by matters_helpers
  (`iframe[title="angularjs"]` -> `#vue_iframe_layout`).

## 2026-06-09 — Correct conversation assertion (non-vacuous)
- Live exploration showed the matter page's inner Vue frame defaults to the matter
  overview; the conversation is the **first engagements tab**. The assertion now opens
  the client card, clicks the **Conversation** tab (`.tab-title`), waits for the pane
  to load (`.no-results-wrapper, .bubble-row`), then asserts 0 `.bubble-row` and a
  visible `.no-results-wrapper` (replacing the earlier `div.content`/`.no-results-text`
  selectors, which matched nothing and made the assertion vacuous).
- Validated non-vacuousness with a control run (skip mark-as-spam): the same submit
  flow produced a message bubble in the Conversation tab within seconds.
- Submit now confirms the loader `#jquery-loader-background` appears then clears
  (positive proof the submit fired), mirroring legacy `pollPageForLoader`.
- Hard gate: 3 clean focused runs (integration, headless).
