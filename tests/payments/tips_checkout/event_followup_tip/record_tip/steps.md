# BO follow-up tip on a paid event attendance (record)

Migrated from automation-js/features/salsa/tips.feature
Scenario: "create event and add follow up tip from clients list - BO".

Prerequisites are API-seeded in `_setup` (tips app + 10/20/30 BO tips, a paid
`r2p_event` event attendance for `first last`, BO login).

## Actions and assertions

1. Open the paid event attendance payment page.
2. Click **Add a tip**, choose **record**, select a **Custom** tip of `5`, and confirm (Cash).
3. **Assert** the back-office payment page (Payments Received) shows:
   - client_name: `first last`
   - name: `Tip for r2p_event`
   - amount: `$5.00`
   - type: `Cash`
   - items: `r2p_event`
   - tip: `$5.00`
