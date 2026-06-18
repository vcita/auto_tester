# Script: Add Standard Document Template (S3)

Reuses the shared upload/list helpers from the sibling
`tests.tempo.documents.document_templates.documents_helpers` (same UI flow + frame
topology; the s3 vs authenticated difference is the account storage backend, which is
not observable in the standard template list — it is asserted in the grab-link test).

## Frames

- Documents page / My Documents side pane: `iframe[title="angularjs"]`.
- Upload dialog: `iframe[title="angularjs"] -> #vue_wizard_iframe`.

## Actions

1. `upload_to_my_documents(page, path)` → open `/app/documents`, click upload button
   `//div[contains(@class,'upload-button')]//button[@data-qa='add']`, drop the file on
   `[data-qa="vc-dropzone--input"]` (wizard dialog frame), confirm with
   `button[data-qa="vc-footer-Upload"]`.
2. `assert_in_standard_templates(page, name)` → the `.side-pane-name` for the file is
   visible in the My Documents side pane.

## Waits

- `NAV_TIMEOUT` (20s) for angularjs/wizard iframe mounts and side-pane propagation.
- No fixed sleeps.
