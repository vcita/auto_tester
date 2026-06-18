# Script: Grab Document Link (S3)

Reuses the shared grab-link/access helpers from the sibling
`tests.tempo.documents.document_templates.documents_helpers`, plus a local
`documents_s3_helpers.assert_link_is_s3` for the s3 storage-signal assertion.

## Frames

- Documents page / My Documents side pane: `iframe[title="angularjs"]`.
- Upload + copy-link dialogs: `iframe[title="angularjs"] -> #vue_wizard_iframe`.

## Actions

1. `upload_to_my_documents(page, path)` (shared helper).
2. `grab_document_link(page, name)`:
   - hover the `.side-pane-item` for the file, open its actions menu
     (`.my-documents-button`), click `Copy public link`,
   - read the link from the copy-link dialog (`[data-qa="vc-input-modal"]` →
     `.link-container__link`).
3. `assert_link_is_s3(link)` → the link contains `fileStorageType=AWS-S3` (the AWS-S3
   storage backend signal; verified live on integration).
4. `assert_link_accessible(page, link, name)`:
   - open the link in a fresh browser context (no business session),
   - assert the response status `< 400` and the page is not an error page.

## Waits

- `NAV_TIMEOUT` (20s) for iframe mounts, dialog render, and the visitor page load;
  `GRAB_TIMEOUT` (15s) for the slow Angular actions menu / copy-link dialog.
- No fixed sleeps.
