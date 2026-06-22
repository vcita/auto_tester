# Setup: Document Templates (S3)

Mirrors the legacy `document-templates-s3.feature` Background
(`Given user logged in to automatic account`): be logged in to the back-office of an
isolated account using the **default** storage backend. On integration the default
documents storage backend is AWS-S3 (verified live — the grabbed public link carries
`fileStorageType=AWS-S3`), so no feature-flag override is needed; the s3 backend is
asserted directly in the grab-link test.

## Steps

1. Log in to the isolated account (username/password from the account profile).
