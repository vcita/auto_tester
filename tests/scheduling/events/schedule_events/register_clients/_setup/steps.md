# Setup: Register clients to an event

Prepares an isolated account for scenario 1 "register clients to event".

1. Log in to the isolated account.
2. Via API: create a "require to pay" $100 event service (`r2p_event...`), create a
   `user_staff` staff member, and create two clients (`silvan goodbye`,
   `judi babish-moshe`) capturing their client-portal tokens.

The event itself is scheduled through the back office in the test, since the
back-office scheduling UI is the in-scope behaviour being migrated.
