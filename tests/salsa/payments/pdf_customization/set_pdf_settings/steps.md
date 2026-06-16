# Set PDF Customization - Steps

## Objective
Set the PDF customization template, logo size, and brand color type in Billing & Invoicing
settings, then verify the values persist after a reload.

Migrates automation-js `pdf-customization.feature` scenario
`set template, logo size, and brand color type`.

## Prerequisites
- Logged in to the isolated account (from `_setup`).
- PDF customization at default settings.

## Steps
1. Open the PDF customization settings tab.
2. Set the template to `modern`.
3. Set the logo size to `Small`.
4. Set the brand color type to `custom`.
5. Save the settings.
6. Reload the settings page and read back the persisted values.
7. Verify the persisted settings are exactly: template `modern`, logo size `Small`,
   brand color type `custom`, brand color `#000000`.

## Expected Result
- All four persisted values match the expected set after the reload.
