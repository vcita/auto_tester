# Setup — Upgrade In Frontage

1. Block the Recurly trust-seal script across the browser context (otherwise the
   later checkout page hangs and its hosted card fields never mount).
2. Log in to the isolated Trial account (created by the runner with
   `package_subscription_id: 28`).
