# Changelog: Grab Document Link (S3)

## 2026-06-18 — Initial migration (VCITA2-14225)

Migrated from automation-js `features/steps/document-templates-s3.feature` scenario
`Grab document link (s3)`.

### Scope

- Upload `clientDoc.pdf` to My Documents (default AWS-S3 backend), grab its public link,
  verify the link is served from S3, and verify a client can access the grabbed link.

### Decisions

- Reuses shared helpers (`upload_to_my_documents`, `grab_document_link`,
  `assert_link_accessible`) from the sibling `document_templates` (authenticated)
  migration — no duplication.
- Adds the s3 storage-signal assertion via local `documents_s3_helpers.assert_link_is_s3`:
  the grabbed link must contain `fileStorageType=AWS-S3`. Verified live on integration —
  the public link is `.../uploads/documents/<id>/clientDoc.pdf?fileStorageType=AWS-S3`.
  This grounds the s3-vs-authenticated distinction in observed behavior and strengthens
  coverage beyond the legacy test (which asserted neither storage type).
- No `documents_upload_to_s3` flag override is needed — AWS-S3 is the default backend on
  integration.
