# Schedule Appointment With Additional Recipients

Migrated from `scheduling-appointments.feature` scenario 2 ("Schedule an appointment from bo
with additional recipients"). Zero scope loss: schedule two appointments adding an additional
recipient (typed email, then chosen "from list") and verify the recipient on each detail page.

## Preconditions (from `_setup`)

- Isolated account, logged in as owner; `service1` and client `Chuck Norris` exist.

## Steps

1. Schedule `service1` for `Chuck Norris`, adding additional recipient `test2+<seq>@vmeetme.com`
   (typed into the additional-recipients combobox; the trailing comma commits the chip).
2. **Verify** the appointment detail shows additional recipient `test2+<seq>@vmeetme.com`.
3. Schedule `service1` for `Chuck Norris` again, this time choosing the recipient **from the
   list** (first existing option in the additional-recipients autocomplete).
4. **Verify** the appointment detail shows additional recipient `test2+<seq>@vmeetme.com`.

## Notes

- The additional-recipients control lives in a collapsible expansion panel
  (`.dialog-expansion-panel__additional-recipients`) inside the Vue scheduling wizard.
- The detail page renders the recipient under `[data-qa='additional-recipients']`.
