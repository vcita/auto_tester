# Grab Document Link

Migrates automation-js `features/steps/document-templates-auth.feature` scenario
`Grab document link (authenticated)`.

## Preconditions

- Logged in to the isolated account (setup).

## Steps

1. Upload the document `clientDoc.pdf` to My Documents.
2. Grab the public link of `clientDoc.pdf` (Copy public link).
3. Access the grabbed link as a client (no business session).

## Expected results

- The grabbed link opens successfully for a client (publicly accessible, no error page).
