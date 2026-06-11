# Attach Document to Saved and Sent Invoice

Migrates automation-js `features/steps/attach-document-to-invoice.feature` scenario
`Attach document to invoice`.

## Preconditions (API)

- Logged in to the isolated account (setup).
- A client exists.
- A "display a fee" service (price 10) exists.

## Steps

1. Upload the document `clientDoc.pdf` to My Documents.
2. Create a new invoice titled `saved_invoice` for the client with the service line
   item, attach the document, and save it as a draft.
3. Open the saved invoice and confirm the document `clientDoc.pdf` is attached.
4. Create a new invoice titled `send_invoice` for the client with the service line
   item, attach the document, and send it.
5. Open the sent invoice and confirm the document `clientDoc.pdf` is attached.

## Expected results

- The document `clientDoc.pdf` is attached to the saved (draft) invoice.
- The document `clientDoc.pdf` is attached to the sent invoice.
