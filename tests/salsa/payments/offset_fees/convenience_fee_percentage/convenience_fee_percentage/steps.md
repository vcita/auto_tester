# Convenience Fee Percentage

## Objective
Verify that a percentage convenience fee (2%) configured in payment settings is
shown at the client-portal checkout and reflected in the payment total and Back
Office.

## Prerequisites
Setup has connected a mock gateway, enabled ACH, saved a card on the client, and
scheduled a past $100 appointment.

## Steps
1. Enable a convenience fee, format percentage, value 2, and save.
2. Open the client portal as the client and open the past appointment's Pay action.
3. Press Pay to open the checkout.
4. Verify the selected card shows the fee badge `+ 2%`.
5. Verify the checkout summary shows fee row `Convenience fee` `$2.00`.
6. Verify the checkout shows a processing-fee line.
7. Proceed to payment and verify the success page shows `Amount received: $102.00`.
8. In Back Office, open the payment and verify client `first last`, name
   `Payment for <service>`, amount `$102.00`, item `<service>`, fee `$2.00`.

## Expected Result
The 2% convenience fee is shown at checkout, charged ($102 total), and reflected
on the Back Office payment page.
