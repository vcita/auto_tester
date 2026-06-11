# Setup — Events List page (isolated account)

Mirrors the legacy events-list.feature Background:
`user logged in to "events list" page in automatic account via API` +
two `user creates new service via API` steps.

## WHAT this setup does

1. Log in to the fresh isolated account (UI session for the test that follows).
2. Create two **event** services via API (legacy used API service creation):
   - `r2p_event<seq>` — payment_setting "require to pay" (charge_type `paid_force`), price 1.
   - `daf_event<seq>` — payment_setting "display a fee" (charge_type `paid_non_secured`), price 1.
   Each creation is confirmed with an independent GET read-back before the test runs.
3. Store the created service names in `context["events_list"]` for the test.

No events are scheduled here — scheduling from the events list page is the in-scope UI
behavior exercised by the test (`list_states`).
