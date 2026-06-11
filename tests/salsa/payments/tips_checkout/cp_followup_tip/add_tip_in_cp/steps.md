# CP follow-up tip on a paid meeting

Migrated from automation-js/features/salsa/tips.feature
Scenario: "take followup tip in cp"

Prerequisites are API-seeded in `_setup` (tips app + 55/66/77 CP tips, `require`/`suggest`
services, two past appointments for `first last`, a recorded $100 payment for the
`require` meeting, BO login + mock gateway connected).

## Actions and assertions

1. As client `first last`, open the client portal, go to Bookings, switch to the Past tab,
   and open the `require` meeting.
2. Click **Add a tip**, select the `66%` tip in the follow-up tip bar, and pay via the
   mock payment gateway popup.
3. **Assert** the client-portal payment success page shows:
   - title: `Thank you for tipping!`
   - amount: `Amount received: $66.00` (66% of the $100 meeting)
