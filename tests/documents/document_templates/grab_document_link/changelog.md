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
