# Script: Grab Document Link

Implemented in `documents_helpers.py`.

## Frames

- Documents page / My Documents side pane: `iframe[title="angularjs"]`.
- Upload + copy-link dialogs: `iframe[title="angularjs"] -> #vue_wizard_iframe`.

## Actions

1. `upload_to_my_documents(page, path)` (see add_standard_template).
2. `grab_document_link(page, name)`:
   - hover the `.side-pane-item` for the file, open its actions menu
     (`.my-documents-button`), click `Copy public link`,
   - read the link from the copy-link dialog (`[data-qa="vc-input-modal"]` →
     `.link-container__link`).
3. `assert_link_accessible(page, link, name)`:
   - open the link in a fresh browser context (no business session),
   - assert the response status `< 400` and the page is not an error page.

## Waits

- `NAV_TIMEOUT` (20s) for iframe mounts, dialog render, and the visitor page load.
- No fixed sleeps.
