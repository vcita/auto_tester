# Changelog — send_message

## 2026-06-05 — Initial migration (VCITA2-13798)
- Migrated from `automation-js/features/steps/crm-bulk-actions.feature` scenario
  "Send message from CRM".
- Created `steps.md`, `script.md`, `test.py`.
- Flow: create 2 clients via account API → open `/app/clients` → select `first02 last02`
  → bulk "Message" (subject "hi", content "hello") → verify the last conversation
  bubble subject/content on the client card.
- Message dialog in `#vue_wizard_iframe`; body is a contenteditable div (focus + type).
  Conversation bubble in `#vue_iframe_layout`. Verified live on integration before coding.
- Waits ≤5s, no fixed sleeps; bubble propagation uses bounded reload-and-recheck (≤2 retries).
