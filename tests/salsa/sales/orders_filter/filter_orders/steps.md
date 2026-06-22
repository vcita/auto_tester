# Filter orders by payable type

Verifies the back-office Orders (Billing & Invoicing) type filter against a paid
booking and a purchased package.

## Prerequisites (subcategory _setup)
- Logged in to the isolated account.
- Client "first last" created via API.
- Paid service "service" ($100, "require to pay") created via API.

## Steps
1. Schedule an appointment for "service" with "first last" via API (creates a
   payable booking order).
2. Open Orders and filter by **bookings** → the list shows exactly **service**.
3. Create the package "test_package" via API (1 service "service", 2 credits,
   $150, specific) and assign it to the client via API (creates a "Package
   purchased" order).
4. Filter by **packages** → the list shows exactly **test_package - Package purchased**.
5. Filter by **bookings + packages** → the list shows exactly
   **test_package - Package purchased** then **service** (order matters).
6. Filter by **invoices** → the list is empty (no invoices exist; no error).
