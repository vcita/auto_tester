# Changelog: Attach Document to Saved and Sent Invoice

## 2026-06-11 — Initial migration (VCITA2-14061)

Migrated from automation-js `features/steps/attach-document-to-invoice.feature`
(scenario `Attach document to invoice`).

### Scope

- Upload `clientDoc.pdf` to My Documents.
- Create + save a draft invoice with the document attached; verify the attachment.
- Create + send an invoice with the document attached; verify the attachment.

Full file: the legacy feature has a single scenario (the title mentions estimates but
only the invoice scenario exists). No scope dropped.

### Decisions

- Reuses the migrated invoice wizard helpers (`invoice_billing_ui.py`) for
  open/new-invoice, client pick, title, line items, and first-invoice-setup handling.
- Fixture: reuses the proven `clientDoc.pdf` upload fixture (the legacy used `pic.jpg`;
  the file is arbitrary — the assertion is on the attached file name, which we control).
- Service created via API as the legacy "display a fee" service (`charge_type=
  paid_non_secured`, price 10) and added to each invoice as a line item.
- Draft save uses the wizard secondary action; send uses the primary action — both
  navigate to the invoice detail, where the attached-document row is asserted.

### Live-iteration findings (integration)

- Uploaded files land in the "MY DOCUMENTS" side pane (`.side-pane-name`, angularjs
  frame), not the shared/internal list (`#vue_iframe_main`) — verification reads the
  side pane.
- The invoice "Attached Documents" section is expanded by default; we target the
  "+ Add Document" button directly (clicking the section header would collapse it).
- The "Add/Share Document" picker is an Angular Material `md-dialog` in the angularjs
  frame (not the Vue wizard frame); the file is chosen from a single `md-select` and
  confirmed with ADD.
- The "From" billing address is a required field on a fresh account, so it is set
  reliably (expand fold → edit → fill → collapse to commit) before save/send.

### Review (Bugbot) + stability

- Bugbot (medium): replaced the shared `_handle_first_invoice_setup` (which set its
  "handled" flag before checking the dialog, so a draft-save call could prevent a later
  send from dismissing the numbering modal) with a stateless `_dismiss_first_invoice_setup`
  run after every save/send.
- Stress: 10/10 (100%) on integration, `--iterations 10` — stamped stable.
