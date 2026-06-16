# Set PDF Customization - Script

## Initial State
- Logged in to the isolated account; PDF customization at defaults.

## Scopes / Locators
- Frontage angular app: `iframe[title="angularjs"]`; settings controls live in the nested
  vue iframe `#vue-app-tab`. Controls are resolved by scanning the page and every frame
  (`_scan`), robust to the nested-iframe depth.
- Template gallery: hover tile `[data-qa="{name}-pro"]` to reveal `[data-qa="{name}-select"]`;
  click select. Selected template read from `.vc-gallery-item--selected` `data-qa`
  (segment before `-`).
- Logo size: open dropdown `.logo-size-container.VcSelectField .v-input__slot`, click the
  `.v-list-item__title` option whose text equals the size. Selected size read from
  `.logo-size-container .selection-text` text.
- Brand color type: radio `[data-qa="radio-{type}"]`. Selected type read from
  `.v-item--active .label-container` `data-qa` (segment after `-`).
- Brand color value: `[data-qa="brand-color-value-container_input"]` input value.
- Save (angular page, outside the vue iframe): `button[data-qa="action-button-payments_settings-save"]`,
  then wait for the settings persist response (`/v2/settings`) to return 2xx.

## Actions
### Step 1: Open PDF customization
- Navigate to `/app/settings/billing_and_invoicing?tab=pdf_customization`; wait for the
  selected template gallery item to render.

### Step 2: Set template / logo size / brand color type
- Hover the `modern` tile, click its select button.
- Open the logo size dropdown, click the `Small` option.
- Click the `custom` brand color radio.

### Step 3: Save
- Click Save; wait for the `/v2/settings` 2xx persist response.

### Step 4: Reload and read back
- Re-navigate to the tab (verifies true persistence, unlike the legacy same-page re-read).
- Read template, logo size, brand color type, and brand color value.

### Step 5: Verify
- Assert the read-back dict equals `{template: modern, logo_size: Small,
  brand_color_type: custom, brand_color: #000000}`.

## Success Verification
- The reloaded settings match the expected set exactly.

## Waits / Stability
- Explicit condition waits replace fixed sleeps: gallery render after navigation, the
  visible select button after hover, the dropdown option text match, and the 2xx save
  response after Save. The read-back navigates fresh, so a silent no-op save is caught.
- data-qa selectors for all actions; read-back uses existing stable legacy CSS
  (`.vc-gallery-item--selected`, `.logo-size-container .selection-text`,
  `.v-item--active .label-container`) which have no data-qa equivalent.
