# Setup: Document Templates

Mirrors the legacy `document-templates-auth.feature` Background: be logged in to the
back-office of an isolated account. (The legacy test denies the
`documents_upload_to_s3` feature flag for fenv compatibility; on integration the
default upload path works, verified live, so no flag override is needed.)

## Steps

1. Log in to the isolated account (username/password from the account profile).
