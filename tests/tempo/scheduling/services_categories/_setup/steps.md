# Setup — Categories & services (isolated account)

Mirrors the legacy categories-and-services.feature Background:
`user logged in to "services settings" page in automatic account via API`.

## WHAT this setup does

1. Log in to the fresh isolated account (UI session for the test that follows).
2. Navigate to the Services index settings page (`/app/settings/services`).
3. Verify the three default services the scenario asserts against are present —
   `Demo class / event`, `In-office appointment`, `Introductory phone call` — so the
   run fails fast with a clear message if the account template ever changes.

No categories or services are created here — every create/edit/move/clone/delete is the
in-scope UI behavior exercised by the test (`manage_categories_services`).
