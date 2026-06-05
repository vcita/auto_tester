# Changelog — share_document

## 2026-06-05 — Initial migration (VCITA2-13798)
- Migrated from `automation-js/features/steps/crm-bulk-actions.feature` scenario
  "Share document from CRM".
- Created `steps.md`, `script.md`, `test.py`.
- Flow: create 2 clients via account API → open `/app/clients` → select all pages →
  bulk "Share document" (`clientDoc.pdf`, notify by email) → verify document in the
  current client's card conversation → verify status "PENDING REVIEW" on documents page.
- Selectors and the nested-iframe topology (CRM top-level; share dialog in
  `#vue_wizard_iframe`; conversation in `#vue_iframe_layout`; documents in
  `#vue_iframe_main`) verified live on integration before coding.
- Waits ≤5s, no fixed sleeps; conversation/document propagation uses bounded
  reload-and-recheck (≤2 retries).

## 2026-06-05 — Status assertion made viewport-agnostic (validation fix)
- The documents list renders a desktop or mobile docuform item based on the inner
  `#vue_iframe_main` Vuetify breakpoint (`mdAndUp`). Both expose
  `data-qa="docuform-status"`, but desktop shows the full label ("Pending review")
  while mobile shows the short label (`document.short_status.pending_review` = "Pending").
  The runner's documents iframe is below `md`, so it rendered "Pending" and the
  exact-match assertion failed.
- Root cause traced through `frontage` `DocuformListItem{Desktop,Mobile}.vue` +
  `statusService.js` (backend status "Pending" → PendingReview when no signature)
  and `document.en.yml`.
- Fix: assert the pending-review state against both renderings
  (`PENDING_REVIEW_LABELS = ("PENDING REVIEW", "PENDING")`). The shared plain
  document is always `pending_review` (no signature → never `pending_approval`),
  so accepting either label is unambiguous for this flow.
