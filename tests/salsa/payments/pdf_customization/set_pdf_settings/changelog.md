# Changelog - Set PDF Customization

## 2026-06-08 - Initial migration (VCITA2-13989)
- Migrated automation-js `features/steps/payments-settings/pdf-customization.feature`
  (1 scenario) into `tests/payments/pdf_customization/set_pdf_settings`.
- Mapped the legacy `pdfCustomization.js` page object to a frame-scan helper
  (`pdf_customization_helpers.py`): set template (hover tile + click select), set logo size
  (dropdown option by text), set brand color type (radio), save (wait for `/v2/settings`
  2xx), and read-back of all four values.
- Quality improvement over legacy: the read-back reloads the settings page (the legacy
  re-read the same already-loaded page), proving true persistence.
- Account profile: isolated (cleanup always), mirroring `taxes_settings` (same host page).
- No client/service/API setup needed (settings-only scenario).
