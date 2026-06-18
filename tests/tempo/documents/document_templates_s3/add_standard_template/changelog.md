# Changelog: Add Standard Document Template (S3)

## 2026-06-18 — Initial migration (VCITA2-14225)

Migrated from automation-js `features/steps/document-templates-s3.feature` scenario
`Adding standard and signature document template (s3)`.

### Scope

- Upload `clientDoc.pdf` to My Documents (default AWS-S3 storage backend); verify it
  appears in the standard template list.
- The legacy signature-template assertion is commented out in the source feature, so it
  is not in scope (no coverage dropped).

### Decisions

- Reuses shared upload/list helpers from the sibling `document_templates`
  (authenticated) migration — same UI flow + frame topology, no duplication.
- The s3-vs-authenticated distinction (storage backend) is not observable in the
  standard template list, so this scenario asserts the same user-visible outcome as the
  authenticated sibling; the s3 storage signal is asserted in the `grab_document_link`
  test (`fileStorageType=AWS-S3` on the public link).
- Fixture: `clientDoc.pdf` (the file is arbitrary; the assertion is on the listed name).
- No `documents_upload_to_s3` flag override is needed — AWS-S3 is the default backend on
  integration (verified live).
