# Manage Taxes - Script

## Initial State
- Logged in to the isolated account; on the dashboard (or wherever `_setup` left the page).
- The account has no taxes.

## Scopes / Locators
- Frontage angular app: `iframe[title="angularjs"]`.
- Tax rows live in the nested vue iframe `#vue-app-tab` (fallback to the angular scope if absent).
- Tax row marker: `div[data-qa="line-tax-{name}-{rate}"]` (new empty row is `line-tax-undefined-undefined`).
- Name input: `input[data-qa="tax-name"]`; rate input: `input[data-qa="tax-rate"]` (scoped per row).
- Add: `.add-tax`. Delete: `[data-qa="tax-delete"]` then confirm `[data-qa="tax-menu-actions-0"]`.
- Save (in the angular page, outside the vue iframe): `button[data-qa="action-button-payments_settings-save"]`,
  then wait for the persisting response (`.../payments/v1/tax_bulk` for create/edit/delete,
  `.../v2/settings` for the tax-mode change) to return 2xx.
- Tax mode radios: `[data-qa="radio-include"]` / `[data-qa="radio-exclude"]`; selected mode read from
  `.v-item--active .label-container` `data-qa` (`radio-{mode}`).

## Actions
### Step 1: Open Taxes settings
- Navigate to `/app/settings/billing_and_invoicing?tab=taxes`; wait for the `.add-tax` button.
- Fallback: if the button does not appear, click the `Taxes` tab and re-resolve the scope.

### Step 2: Create two taxes
- For each tax: click `.add-tax`, wait for the new empty row `line-tax-undefined-undefined`,
  resolve its `tax-name` and `tax-rate` input element handles up front (handles survive the
  row's data-qa mutation), set the name then the rate, and wait for the row
  `line-tax-{name}-{rate}` to materialize.
- Click Save and wait for the `tax_bulk` save response (2xx).

### Step 3: Verify list == [taylor swift 1-13, taylor swift 2-13.13131]
- Read all `line-tax-*` row `data-qa` values (excluding the empty placeholder row) and assert exact match.

### Step 4: Edit taylor swift 1 -> taylor swift 13 / 13.14
- Clear+type the new name into the `tax-name` input of row `line-tax-taylor swift 1-13`.
- Clear+type the new rate into the `tax-rate` input of row `line-tax-taylor swift 13-13`.
- Wait for row `line-tax-taylor swift 13-13.14`; click Save.

### Step 5: Verify list == [taylor swift 13-13.14, taylor swift 2-13.13131]

### Step 6: Delete taylor swift 13 / 13.14
- Click `tax-delete` in the row, confirm `tax-menu-actions-0`, wait for the row to disappear; click Save.

### Step 7: Verify list == [taylor swift 2-13.13131]

### Step 8: Change tax mode to include
- Click `[data-qa="radio-include"]`; click Save.

### Step 9: Verify selected tax mode == include
- Read `.v-item--active .label-container` `data-qa`; the segment after `radio-` must be `include`.

## Success Verification
- All three list assertions match exactly.
- The selected tax mode is `include`.

## Waits / Stability
- Explicit condition waits replace fixed sleeps: row data-qa materialization after typing, the 2xx
  save response after each Save, and a short poll (up to 5s) when asserting the list to absorb reactive
  re-render. `edit_tax` retries if the post-save Vue re-render detaches a resolved row handle.
- data-qa selectors throughout; no PGW or feature flag required.
