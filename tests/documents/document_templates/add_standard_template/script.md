# Script: Add Standard Document Template

Implemented in `documents_helpers.py`.

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
