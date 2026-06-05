# Setup — Orders Filter (isolated account)

Mirrors the legacy orders.feature Background (all API), on a fresh isolated account.

1. Log in to the isolated account (UI session is needed for the Orders back-office view).
2. Create the client "first last" (`test+<ts>@vmeetme.com`) via API.
3. Create the appointment service "service" priced $100 with "require to pay"
   (charge_type `paid_force`) via API.

Saves to context: `orders_client`, `orders_service` (id/name/price/currency).
