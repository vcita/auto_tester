# Paying for appointment (partial then full)

Migrated from `appointment-payments.feature` scenario 3 "paying for appointment".

## Steps

1. Record a $10 payment against the appointment's payment request.
   - The request becomes **DUE $90.00 (out of $100.00)** for "first last".
   - Payments Received, filtered by "first", shows one **Payment for service** row.
2. Record a $90 payment against the same request.
   - The request becomes **PAID $100.00**.
   - Payments Received, filtered by "first", shows two **Payment for service** rows.
