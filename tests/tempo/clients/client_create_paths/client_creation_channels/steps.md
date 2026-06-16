# Create Client Through All Channels

Migrated from `automation-js/features/steps/client-create-new-CRM.feature`
(Scenario: "creation of a client - new CRM").

## Preconditions (setup)
- Logged in to the isolated automatic account (the business owner).

## Steps & expected outcome

1. **New-CRM dialog**: create a client `first last` (`test+<seq>@vmeetme.com`) via the
   `+ New` client dialog. Search `first` in the CRM All tab → a row `first last` shows.
2. **API**: create a client `api_first api_last` (`testapi+<seq>@vmeetme.com`) via API.
   Search `api_first` in the CRM All tab → a row shows.
3. **Livesite leave-details**: as a public visitor, leave details on the business
   livesite (subject `Hi Contact Request`, message `hello`, to the business email,
   `form_first form_last`).
   - The client receives an email `Thank you for your message`.
   - The business receives an email `Hi Contact Request`.
   - Search `form_first` in the CRM All tab → a row shows.
   - The conversation `Hi Contact Request` is visible in the client portal.
4. **Contact-form widget**: submit the widget (`widget_first widget_last`,
   `widget@vmeetme.com`, message `hello`).
   - The client receives an email `Thank you for your message`.
   - The business receives an email `Message from widget_first widget_last`.
   - Search `widget_first` in the CRM All tab → a row shows.
