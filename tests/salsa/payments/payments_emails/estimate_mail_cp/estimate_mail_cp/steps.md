# Client receives estimate mail, and opens CP page

Migrated from `payments-emails.feature` scenario 6 "Client receives estimate mail,
and opens CP page".

## Steps

1. Create an estimate **bestimate** for the client via API with **send_email = true**,
   billing address **Babylon, persia**, item **product21**.
   - The client receives an email with subject **New estimate from Automation test
     business** (business name dynamic on isolated accounts; prefix asserted).
2. Open the client portal from the **New estimate from ...** email link.
   - The CP estimate page displays:
     - title **bestimate #0000001**
     - price **10 USD**
     - client **first last**
     - status **pending_client_action** (APPROVE / REJECT actions)
     - item **product21** (description **description for payable item21**, price **10**).
