# Schedule appointment with packaged service

Migrated from `appointment-payments.feature` scenario 6
"Schedule appointment with packaged service".

## Steps

1. Mark **meeting1** as completed; its payment request becomes **DUE $100.00**
   (not redeemed).
2. Mark **meeting2** as completed and redeem it with the **package**; its payment
   request becomes **PAID $0.00**, redeemed with package **package**.
3. Cancel **meeting2**'s package redemption; its payment request returns to
   **DUE $100.00** with the package credit refunded.
