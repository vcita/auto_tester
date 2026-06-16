# Setup: Event Follow-up Tip

Mirrors tips.feature scenario "create event and add follow up tip from clients list - BO".

1. Enable tips feature flags.
2. Assign the `tips` app (Admin auth).
3. Set tip options `10,20,30` + enable tips for BO (POST /platform/v1/payment/settings, read-back).
4. Create client `first last`.
5. Create a require-to-pay event service `r2p_event` ($10) and schedule an event for it.
6. Register `first last` to the event.
7. Record a $10 Cash payment for the attendance via API so it is fully paid
   (prerequisite for the event "Add a tip" follow-up action).
8. Log in to the back office.
