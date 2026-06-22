# Setup: Event payment request lifecycle (isolated account)

Mirrors the legacy `event-payments.feature` Background.

## What it does
1. Log in to the fresh isolated account.
2. Via API: create client `first last`, a "require to pay" ($10) **event** service, schedule an event instance, and register the client as an attendee.

The isolated account keeps the event and its single payment request deterministic.
