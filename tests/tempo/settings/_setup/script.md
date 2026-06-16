# Settings Category Setup — Script

1. `update_business_country(context, "Israel")` — admin-less POST to
   `/platform/v1/businesses/{uid}` with `{business:{business:{country_name}}}`.
2. `fn_login(page, context, username, password)` — UI login.
