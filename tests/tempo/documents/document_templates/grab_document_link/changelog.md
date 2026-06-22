# Changelog: Grab Document Link

## 2026-06-11 — Initial migration (VCITA2-14062)

Migrated from automation-js `features/steps/document-templates-auth.feature` scenario
`Grab document link (authenticated)`.

### Scope

- Upload `clientDoc.pdf` to My Documents, grab its public link, and verify a client can
  access the grabbed link.

### Decisions

- Reuses the document-upload flow verified live during the attach-document-to-invoice
  migration.
- The grabbed link is accessed in a fresh browser context (no business session), which
  matches the legacy `client accesses grabbed link` step and proves true public access.
- Verification asserts the link loads with HTTP < 400 and is not an error page (the
  legacy step only navigated and waited for idleness, with no content assertion).

### Fixes during migration

- `grab_document_link`: the desktop My-Documents actions row exposes both a Share button
  and a kebab (⋮) menu under `.side-pane-actions`. The first generic `.my-documents-button`
  hit the Share button, so the selector was narrowed to the kebab
  (`button.my-documents-button:has(md-icon.icon-dots-three-vertical)`) before choosing
  "Copy public link".
- Bugbot (medium): clarified the public-link error-page check to use an explicit set of
  error markers instead of a `or`/`and` chain whose precedence was easy to misread.
