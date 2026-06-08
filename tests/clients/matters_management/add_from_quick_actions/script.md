# Add Matter From Quick Actions - Script

> Status: Verified live on integration 2026-06-08 (VCITA2-13952)

## Initial State
- Logged in; on an app page (contact matter page from previous test); `contact_client_email` in context.

## Actions (`matters_helpers.add_matter_from_quick_actions`)
1. Top POV page: click `[data-qa='vcMenu-QuickAction']` → click `[data-qa='item-client']` ("Add client").
2. Dialog renders in outer Angular frame (`iframe[title="angularjs"]`):
   - click `input[name='email']`, then fill `#autocomplete-email` with the contact email.
   - click the suggestion `get_by_text(contact_email, exact=True)`.
   - "This email already exists" popup: force-click the radio
     `md-radio-button[aria-label="Create a new client under this contact"]`
     (Angular-Material ripple intercepts a normal click; the text label is not the
     pointer target — a normal/text click hangs to a 30s timeout).
   - confirm the choice (`button[ng-click='ok()']`), then click the second
     "add client under <contact>" confirm (`button[ng-click='continue()']`) ONLY if it
     appears — it is absent when the contact already has a matter (e.g. matter_1 from the
     previous test), so confirmations are dismissed resiliently in a 5s-bounded loop that
     returns once the matter form is reachable.
3. First name pre-populates (`input[name='first_name']`); fill matter name
   `f-client-field[field*='matterName'] input` = `matter_2` (typed with real keystrokes
   so Angular `ng-model` commits); click `button:has-text('Save')`.

## Verification (`assert_matter_under_contact`)
- Open contact matter page; inner `.matter-list-row` contains `matter_2`; contact email matches.

## Selector notes
- Quick Actions menu/items expose stable `data-qa` (`vcMenu-QuickAction`, `item-client`).
- The suggested-contact dialog (legacy Angular) has `#autocomplete-email`; radio uses text.
