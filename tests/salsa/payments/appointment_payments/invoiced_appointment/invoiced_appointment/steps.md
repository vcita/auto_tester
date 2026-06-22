# Paying for invoiced appointment

Migrated from `appointment-payments.feature` scenario 5
"Paying for invoiced appointment".

## Steps

1. Invoice the appointment (invoice name **appointment_invoice**, billing
   address "blablablabla").
2. Pay the invoice **appointment_invoice #0000001** for **$100**.
3. The appointment's payment request becomes **PAID $100.00** for "first last"
   on "service".
4. Payments Received shows **Payment for appointment_invoice #0000001**.
