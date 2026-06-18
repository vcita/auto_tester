# Add Standard Document Template (S3)

Migrates automation-js `features/steps/document-templates-s3.feature` scenario
`Adding standard and signature document template (s3)` (standard template part; the
signature template assertion is commented out in the legacy feature).

The account uses the default (AWS-S3) documents storage backend.

## Preconditions

- Logged in to the isolated account (setup).

## Steps

1. Upload the document `clientDoc.pdf` to My Documents.
2. Confirm `clientDoc.pdf` appears in the standard (My Documents) template list.

## Expected results

- `clientDoc.pdf` is listed as a standard document template.
