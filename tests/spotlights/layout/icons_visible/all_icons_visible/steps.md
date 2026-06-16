# All Icons Visible Across Frontage Pages

Migrates automation-js `features/spotlights/icons.feature`
(`Scenario: Icons shown in all the iframes`).

## Preconditions
- Logged in (category `_setup`, with `new_dashboard` enabled).

## Steps
1. Navigate to the **new dashboard** page.
   - Assert all icons are visible on the `dashboard` page (POV layer).
2. Navigate to the **inbox** page.
   - Assert all icons are visible on the `inbox` page (POV + Angular layers).
3. Navigate to the **calendar** page.
   - Assert all icons are visible on the `calendar` page (POV + Vue layers).
4. Navigate to the **CRM** page.
   - Assert all icons are visible on the `CRM` page (POV layer).

## "All icons are visible" means
For each page, for every iframe layer mapped to that page, every design-system
icon present in the DOM must be rendered (visible). Any icon that exists but is
not displayed (broken/missing render) is a failure; the test reports the offending
icon identifiers.

Icon selectors per layer (mirrors the legacy `Layout` page object):
- POV: `[data-qa="VcIcon"]` excluding `data-exclude-icon-test` wrappers and `.draggable-tabs`.
- Angular: `md-icon` excluding `f-help-center md-icon`.
- Vue: `[data-qa="VcIcon"]` excluding `data-exclude-icon-test` wrappers.
