# Grab Document Link (S3)

Migrates automation-js `features/steps/document-templates-s3.feature` scenario
`Grab document link (s3)`.

The account uses the default (AWS-S3) documents storage backend, so the grabbed public
link is served from S3 (carries the `fileStorageType=AWS-S3` signal). This is the
defining distinction of the legacy s3 feature vs the authenticated sibling.

## Preconditions

- Logged in to the isolated account (setup).

## Steps

1. Upload the document `clientDoc.pdf` to My Documents.
2. Grab the public link of `clientDoc.pdf`.
3. Confirm the grabbed link is served from the AWS-S3 backend.
4. Confirm a client (no business session) can access the grabbed link.

## Expected results

- The grabbed public link carries the AWS-S3 storage signal.
- The link opens successfully for an unauthenticated visitor (not an error page).
