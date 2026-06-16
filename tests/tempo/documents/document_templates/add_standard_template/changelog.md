# Changelog: Add Standard Document Template

## 2026-06-11 — Initial migration (VCITA2-14062)

Migrated from automation-js `features/steps/document-templates-auth.feature` scenario
`Adding standard and signature document template (authenticated)`.

### Scope

- Upload `clientDoc.pdf` to My Documents; verify it appears in the standard template
  list.
- The legacy signature-template assertion is commented out in the source feature, so it
  is not in scope (no coverage dropped).

### Decisions

- Reuses the document-upload flow + frame topology verified live during the
  attach-document-to-invoice migration.
- Fixture: `clientDoc.pdf` (the file is arbitrary; the assertion is on the listed name).
- The legacy `documents_upload_to_s3` deny flag is omitted — the default upload path
  works on integration (verified live), so no flag override is needed.
