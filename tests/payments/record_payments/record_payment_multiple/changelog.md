# Changelog

## 2026-05-19 - Stabilize Multiple Payments Workflow
**Phase**: Test
**Author**: Cursor AI
**Reason**: Full payments stress runs intermittently timed out after the first payment and fixed amounts broke taxed invoices.
**Changes**:
- Created a fresh invoice for the test instead of relying on previous workflow state.
- Calculated the second payment from the actual remaining invoice balance.
- Added robust record-payment dialog opening across page and iframe scopes.
- Waited for the balance to update before recording the second payment.
- Force-clicked the final Record action to avoid transient Angular actionability issues.
