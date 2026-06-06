# Setup: ad-hoc sale + refund

Isolated account (fresh per run) so the order/payment are deterministically
numbered `Sale #1`.

1. Log in to the isolated account (back office).
2. Create the client "first last" via API with a unique email. The make-payment
   form later uses that same email so the sale is attributed to "first last".
